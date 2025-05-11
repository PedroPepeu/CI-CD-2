import json
import psycopg2
import os
import time
from datetime import datetime
from pathlib import Path

def collect_performance_metrics(conn):
    """Collect various database performance metrics"""
    metrics = {}
    
    with conn.cursor() as cur:
        # Query execution times
        cur.execute("""
            SELECT query, calls, total_time, mean_time
            FROM pg_stat_statements
            ORDER BY total_time DESC
            LIMIT 5;
        """)
        metrics['slow_queries'] = [
            {
                'query': row[0],
                'calls': row[1],
                'total_time': row[2],
                'mean_time': row[3]
            }
            for row in cur.fetchall()
        ]
        
        # Index usage statistics
        cur.execute("""
            SELECT
                schemaname || '.' || relname as table,
                idx_scan as index_scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
            LIMIT 5;
        """)
        metrics['index_usage'] = [
            {
                'table': row[0],
                'index_scans': row[1],
                'tuples_read': row[2],
                'tuples_fetched': row[3]
            }
            for row in cur.fetchall()
        ]
        
        # Table statistics
        cur.execute("""
            SELECT
                relname as table,
                n_live_tup as live_rows,
                n_dead_tup as dead_rows,
                last_vacuum,
                last_analyze
            FROM pg_stat_user_tables
            ORDER BY n_live_tup DESC
            LIMIT 5;
        """)
        metrics['table_stats'] = [
            {
                'table': row[0],
                'live_rows': row[1],
                'dead_rows': row[2],
                'last_vacuum': row[3].isoformat() if row[3] else None,
                'last_analyze': row[4].isoformat() if row[4] else None
            }
            for row in cur.fetchall()
        ]
    
    return metrics

def generate_report():
    """Generate a performance report for the database"""
    try:
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Connect to database
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test_db")
        conn = psycopg2.connect(db_url)
        
        # Collect metrics
        metrics = collect_performance_metrics(conn)
        
        # Add metadata
        report = {
            'timestamp': datetime.now().isoformat(),
            'database': db_url.split('/')[-1],
            'metrics': metrics
        }
        
        # Save report
        report_file = reports_dir / 'performance.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Performance report generated: {report_file}")
        return str(report_file)
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    try:
        report_path = generate_report()
        print(f"Report generated successfully at: {report_path}")
    except Exception as e:
        print(f"Report generation failed: {str(e)}")
        exit(1) 
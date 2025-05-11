import { add, sub, div, mul } from "../math";

test('add 1 plus 2 equals to 3', () => {
    expected(add(1, 2).toBe(3));
});
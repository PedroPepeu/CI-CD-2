import { add, sub } from "../src/math";

describe('Math test', () => {
    test('add 1 to 2 equals to 3', () => {
        expect(add(1, 2)).toEqual(3);
    });

    test('sub 2 by 1 equals to 1', () => {
        expect(sub(2, 1)).toEqual(1);
    });

    test('Divide 2 by 1 equals to 1', () => {
        expect(div(2, 1)).toEqual(1);
    });

    test('Multiply 2 by 2 equals to 4', () => {
        expect(mul(2, 2)).toEqual(1);
    });
})
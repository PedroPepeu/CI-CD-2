import { add, sub, div, mul } from "../src/math";

describe('Math test', () => {
    test('add 1 plus 2 equals to 3', () => {
        expect(add(1, 2)).toEqual(3);
    });
})
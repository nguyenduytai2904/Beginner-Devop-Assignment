const CalculationOperations = require('./calculator');



describe("Calculation TestCases", () => {

    test("Add 2 numbers", () => {


        var sum = CalculationOperations.Add(1, 2)


        expect(sum).toBe(3);

    });

    test("Subtract 2 numbers", () => {


        var subtract = CalculationOperations.subtract(10, 2)


        expect(subtract).toBe(8);

    });

    test("Multiple 2 numbers", () => {

        var multiple = CalculationOperations.multiple(2, 8)


        expect(multiple).toBe(16);

    });

    test("Divide 2 numbers", () => {


        var divide = CalculationOperations.divide(24, 8)


        expect(divide).toBe(3);

    });

})
package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class CalculatorTest {

    @Test
    public void testAdd() {
        Calculator calculator = new Calculator(new Rounder());
        assertEquals(3, calculator.add(1, 2));
    }

    @Test
    public void testSubtract() {
        Calculator calculator = new Calculator(new Rounder());
        assertEquals(1, calculator.subtract(2, 1));
    }
}

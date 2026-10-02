package com.example;

/** Production class: the subject of CalculatorTest. */
public class Calculator {

    private final Rounder rounder;

    public Calculator(Rounder rounder) {
        this.rounder = rounder;
    }

    public int add(int a, int b) {
        return rounder.round(a + b);
    }

    public int subtract(int a, int b) {
        return rounder.round(a - b);
    }
}

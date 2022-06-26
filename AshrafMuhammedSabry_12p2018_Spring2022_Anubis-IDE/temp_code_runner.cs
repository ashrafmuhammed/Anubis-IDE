using System;

public class MainClass
{
    public static void Main()
    {
        // function call
        Square(5);
    }

    static void Square(int i)
{
    // calculating the square of the input
    int input = i;
    int product = input * input;

    // printing the result
    Console.WriteLine("Result:");
    Console.WriteLine(product);
}
}
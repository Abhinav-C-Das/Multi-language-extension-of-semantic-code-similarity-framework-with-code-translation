public class SumOfDigits {
    public static int sumDigits(int n) {
        int sum = 0;
        int temp = n;
        while (temp > 0) {
            sum += temp % 10;
            temp /= 10;
        }
        return sum;
    }

    public static void main(String[] args) {
        int number = 98765;
        int result = sumDigits(number);
        System.out.println("Sum of digits of " + number + " is " + result);
    }
}

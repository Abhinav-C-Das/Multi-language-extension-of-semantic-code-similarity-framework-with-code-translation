// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int factorial(int n) {
        if ((n <= 1)) {
            return 1;
        }
        return (n * factorial((n - 1)));
    }

    public static void main(String[] args) {
        System.out.println("5! = " + factorial(5));
    }
}

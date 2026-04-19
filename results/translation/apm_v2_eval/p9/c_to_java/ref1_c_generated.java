// Auto-generated from CPG Abstract Program Model
class Ref1 {

    public static int gcd(int a, int b) {
        while ((b != 0)) {
            int temp = b;
            b = (a % b);
            a = temp;
        }
        return a;
    }

    public static void main(String[] args) {
        System.out.println("GCD(48,18) = " + gcd(48, 18));
    }
}

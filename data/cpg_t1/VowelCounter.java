public class VowelCounter {
    public static int countVowels(char[] chars, int length) {
        int count = 0;
        for (int i = 0; i < length; i++) {
            char c = chars[i];
            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
                    c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') {
                count++;
            }
        }
        return count;
    }

    public static void main(String[] args) {
        char[] text = { 'h', 'e', 'l', 'l', 'o', ' ', 'w', 'o', 'r', 'l', 'd' };
        int size = 11;
        int vowels = countVowels(text, size);
        System.out.println("Number of vowels: " + vowels);
    }
}

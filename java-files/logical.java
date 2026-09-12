public class Logic {

    public static void test() {
        boolean first = true;
        boolean second = false;

        if (first && second) {
            return;
        }

        if (first || second) {
            return;
        }

        if (!first) {
            return;
        }
    }
}

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

#define WORDSIZE 5
#define tolower(x) (x | 0x20)

char *dictionary[] = {
    "forte",
    "peril",
    "quant",
    "salad",
    "range",
    "small",
    "large",
    "state",
    "since",
    "order",
    "loops",
    "bytes",
    "nippy",
    "frogs",
    "types"
};


int main(int argc, char **argv) {

    unsigned int seed = 0;
    if (argc > 2) {
        printf("USAGE: %s [seed] (takes input on stdin)\n", argv[0]);
        return 0;
    }
    if (argc == 2) {
        seed = atoi(argv[1]);
        printf("Using provided seed %d\n", seed);
    }

    srand(seed);

    int choice = rand() % (sizeof(dictionary) / sizeof(dictionary[0]));
    char *secret = dictionary[choice];
    printf("[DBG] Secret word is: %s (%d)\n", secret, choice);

    char guess[WORDSIZE] = {0};
    char hits[WORDSIZE] = {0};
    int misses = 0;
    int retval = 0;

    int bytes_read = read(STDIN_FILENO, guess, sizeof(guess));

    if (bytes_read < WORDSIZE) {
        printf("Not enough letters!\n");
        return 0;
    }
    else {

        for (int i=0; i < WORDSIZE; i++) {
            if (tolower(guess[i]) == tolower(secret[i])) {
                hits[i]++;
                guess[i] = 0;
                retval |= 1 << i;
            } else {
                misses++;
            }
        }

        if (misses == 0) {
            printf("You win!\n");
            return -1;
        } else {
            printf("Better luck next time...\n");
        }
        return retval;
    }

}
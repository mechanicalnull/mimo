#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char **argv) {
    char in_buf[40] = {0};
    int bytes_read;

#ifdef STDIN_INPUT
    if (argc != 1) {
        printf("USAGE: %s (input on stdin)\n", argv[0]);
        return -1;
    }
    bytes_read = read(STDIN_FILENO, in_buf, sizeof(in_buf)-1);
#endif
#ifdef FILE_INPUT
    if (argc != 2) {
        printf("USAGE: %s INPUT_FILE\n", argv[0]);
        return -1;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror("open failed:");
        return -1;
    }

    bytes_read = read(fd, in_buf, sizeof(in_buf)-1);

    close(fd);
#endif

    if (bytes_read > 4) {
        if (in_buf[0] == 'F') {
            if (in_buf[1] == 'u') {
                if (in_buf[2] == 'Z') {
                    if (in_buf[3] == 'z') {
                        abort();
                    }
                    return 3;
                }
                return 2;
            }
            return 1;
        }
    }

    return 0;
}
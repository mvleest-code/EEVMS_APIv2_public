from flask import Flask, render_template
import os

app = Flask(__name__)
log_file_path = 'eagle_eye_vms.log'  # Adjust to your log file's path

def tail(f, lines=40):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []  # blocks of size BLOCK_SIZE, in reverse order starting from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number * BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # read the last block we haven't yet read
            f.seek(0,0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b'\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b''.join(reversed(blocks))
    return all_read_text.splitlines()[-total_lines_wanted:]

@app.route('/')
def index():
    with open(log_file_path, 'rb') as f:
        lines = tail(f, 40)
        lines = [line.decode('utf-8') for line in lines]
    return render_template('log.html', lines=lines)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3343)

# curl -F "file=@draft-irtf-icnrg-flic-03.xml" -X POST https://author-tools.ietf.org/api/render/text

import requests
import sys
import getopt


def usage():
    print('usage: render -i input_file -o output_file -f (text | html)')
    print()


def get_args():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:o:f:')
    except getopt.GetoptError:
        usage()
        sys.exit(-2)

    input_file_name = None
    output_file_name = None
    output_format_name = None

    for opt, arg in opts:
        if opt == "-i":
            input_file_name = arg
        elif opt == "-o":
            output_file_name = arg
        elif opt == "-f":
            output_format_name = arg
        else:
            usage()
            sys.exit(-3)

    assert input_file_name is not None
    assert output_file_name is not None
    assert output_format_name is not None

    return input_file_name, output_file_name, output_format_name


def print_logs(output):
    try:
        logs = output['logs']
        errors = logs['errors']
        warnings = logs['warnings']
        if len(errors) > 0:
            print(f'Errors:\n')
            for x in errors:
                print(f'\t{x}')

        if len(warnings) > 0:
            print(f'Warnings:\n')
            for x in warnings:
                print(f'\t{x}')

    except KeyError as e:
        print(f'Output has no key: {e}')


if __name__ == "__main__":

    input_file, output_file, output_format = get_args()

    api_text = f'https://author-tools.ietf.org/api/render/{output_format}'
    with requests.session() as sess:
        files = {'file': open(input_file, 'rb')}
        response = sess.post(api_text, files=files)
        if not response.ok:
            print(f"status = {response.status_code}, reason = {response.reason}")
            print(response.content.decode('utf-8'))
            exit(-1)
        output = response.json()
        print_logs(output)

        try:
            download_url = output['url']
            print(f'Downloading {download_url} as {output_file}')
            rendered = sess.get(download_url)
            with open(output_file,'w') as fh:
                fh.write(rendered.text)
        except KeyError:
            pass

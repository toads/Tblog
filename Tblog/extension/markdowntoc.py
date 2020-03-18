"""
MIT License

Copyright (c) 2018 Alexander Lee
Copyright (c) 2020 toads


Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import re


def get_tags_in_note(md_text):
    """
    Returns a set of tags that exist in the note using the RegEx. Tags are elements that are preceeded by '#'.
    """

    # First, ignore all code blocks since our regex is unable to handle it
    text_no_code = []

    lines_iter = iter(md_text.splitlines())
    in_code_block = False
    for line in lines_iter:
        if line.startswith('```'):
            in_code_block = not in_code_block

        if not in_code_block:
            text_no_code.append(line)

    text_no_code = '\n'.join(text_no_code)

    # Match all tags
    # Positive Lookbehind 1: Start of character
    # Positive Lookbehind 2: newline character or ' '
    # (needs to be separate cause Python only takes fixed-length lookbehinds)
    # Group 1: Starts with '#' and ends with '#' as long as middle is not '#' or a newline character (#tags#)
    # Group 2: Starts with '#' and is not succeeded by a '#', ' ', or newline character (#tags)
    # We need two groups because '#tags#' can have spaces where '#tags' cannot
    tag_matches = re.findall(r'((?<=^)|(?<=\n|\r| ))(#[^#\r\n]+#|#[^#\r\n ]+)',
                             text_no_code, re.MULTILINE)
    tag_matches = map(lambda match: match[1],
                      tag_matches)  # Second Capture Group
    return set(tag_matches)


def has_table_of_contents(md_text):
    """
    Return True or False whether or not a Table of Contents header already exists in the given Markdown text.
    """
    return re.search(r'^#+\sTable\sof\sContents', md_text,
                     re.IGNORECASE | re.MULTILINE) is not None


def get_headers(md_text, max_priority):
    """
    Retrieves a list of header, priority pairs in a given Markdown text.

    Format: (Header Title, Priority)
    """
    lines_iter = iter(md_text.splitlines())

    # Skip the first line because it's the Title
    # next(lines_iter)

    # List of Tuples: (Header Title, Number of #)
    header_priority_pairs = []
    in_code_block = False
    for line in lines_iter:
        if line.startswith('```'):
            in_code_block = not in_code_block

        elif not in_code_block and line.startswith('#') and ' ' in line:
            md_header, header_title = line.split(' ', 1)

            # Check if md_header has all '#'
            if md_header != md_header[0] * len(md_header):
                continue

            # Check if md_header is of lower priority than listed
            if len(md_header) > max_priority:
                continue

            if header_title.lower() != 'table of contents' and len(
                    header_title) > 1:
                header_priority_pairs.append((header_title, len(md_header)))

    return sequentialize_header_priorities(header_priority_pairs)


def sequentialize_header_priorities(header_priority_pairs):
    """
    In a case where a H3 or H4 succeeds a H1, due to the nature of the Table of Contents generator\
    which adds the number of tabs corresponding to the header priority/strength, this will sequentialize\
    the headers such that all headers have a priority of atmost 1 more than their preceeding header.

    [('Header 1', 1), ('Header 3', 3), ('Header 4', 4)] -> [('Header 1', 1), ('Header 2', 2), ('Header 3', 3)]
    """
    # Go through each header and and if we see a pair where the difference in priority is > 1, make them sequential
    # Ex: (H1, H3) -> (H1, H2)
    for i in range(len(header_priority_pairs) - 1):
        header, priority = header_priority_pairs[i]
        next_header, next_priority = header_priority_pairs[i + 1]

        if (next_priority - priority > 1):
            header_priority_pairs[i + 1] = (next_header, priority + 1)

    return header_priority_pairs


def create_github_header_anchor(header_title):
    """
    Returns a Github Markdown anchor to the header.
    """
    return '[{}](#{})'.format(header_title,
                              header_title.strip().replace(' ', '-'))


def create_table_of_contents(header_priority_pairs,
                             toc='# Table of Contents',
                             note_uuid=None):
    """
    Returns a list of strings containing the Table of Contents.
    """
    if len(header_priority_pairs) == 0:
        return None

    bullet_list = [toc]

    highest_priority = min(header_priority_pairs, key=lambda pair: pair[1])[1]
    for header, priority in header_priority_pairs:
        md_anchor = create_github_header_anchor(header)
        bullet_list.append('\t' * (priority - highest_priority) + '* ' + # noqa
                           md_anchor)

    return bullet_list


def create_table_of_contents_github(md_text, toc, header_priority=3):
    """
    Read from file and returns list of (Original Text, Table of Contents List).
    """
    md_text_toc_pairs = []

    header_list = get_headers(md_text, header_priority)
    table_of_contents_lines = create_table_of_contents(
        header_list,
        toc,
    )

    md_text_toc_pairs = (md_text, table_of_contents_lines)

    return md_text_toc_pairs


def find_note_contents_start(md_text_lines):
    """
    Some notes in Bear contain #tags near the title. This returns the index in the list that\
    isn't the title or contains tags. If no index found, return len(md_text_lines)
    """
    # Start at 1 to skip the title
    # Look for regex matches of tags and if lines from the top contain tags, then skip
    for i in range(1, len(md_text_lines)):
        if re.search(r'((?<=^)|(?<=\n|\r| ))(#[^#\r\n]+#|#[^#\r\n ]+)',
                     md_text_lines[i]) is None:
            return i

    return len(md_text_lines)


def toc_prase(md_text: str,
              toc: str = '# Table of Contents',
              header_priority: int = 3):
    """
    @params header priority  # noqa
    (Default: 3) Maximum Header Priority/Strength to consider as Table of Contents 
    @params toc      # noqa        
    (Default: '# Table of Contents') Table of Contents Style
    return toc
    """

    md_text, toc_lines = create_table_of_contents_github(
        md_text, toc, header_priority)

    # Inject Table of Contents (Title, \n, Table of Contents, \n, Content)
    # text_list = md_text.splitlines()
    # content_start = find_note_contents_start(text_list)

    # updated_text_list = [
    #     *text_list[:content_start], '', *toc_lines, '',
    #     *text_list[content_start:]
    # ]
    # Regex extracts anchor text from ancho
    # NOTE: There are edge cases with code blocks, bold, strikethroughs, etc...
    # subtitle_text = re.sub(r'\[([^\[\]]+)\]\([^\(\)]+\)', r'\1',
    #                        ' '.join(updated_text_list[1:]))
    # updated_md_text = '\n'.join(updated_text_list)

    print('\n'.join(toc_lines) + '\n')
    return '\n'.join(toc_lines) + '\n'

#!/usr/bin/env python
import os
from re import search
from shutil import rmtree
from requests import get
from tempfile import mkdtemp
from wand.image import Image
from bs4 import BeautifulSoup
from urlparse import urlparse
# from socket import setdefaulttimeout

def grub(url, output_path=None):
    """Perform complete grub operation."""
    # socket.setdefaulttimeout(20) # used to avoid extra long hangs. Is this necessary?
    OUTPUT_FORMAT = '.pdf'

    # check url validity
    if not check_url(url):
        raise ValueError('The URL requested is not valid.')

    # use current working directory as default if no path is supplied
    if output_path == None:
        output_dir = os.getcwd()
        output_file = ''

    # else split for testing
    else:
        output_dir, output_file = os.path.split(output_path)

    # create directory
    make_dir(output_dir)

    # if no output directory, use current one
    if output_dir == '':
        output_dir = os.getcwd()

    # if no output filename, build from url
    if output_file == '':
        author, title = get_slide_metadata(url)
        output_file = '{}-by-{}{}'.format(title, author, OUTPUT_FORMAT)

    # else check filename for correct format
    elif output_file[-4:] != OUTPUT_FORMAT:
        output_file = '{}{}'.format(output_file, OUTPUT_FORMAT)

    # rebuild output path
    output_path = os.path.join(output_dir, output_file)

    # get html and soup it up
    html = get_html(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    # get the slides img tags
    slides_markup = soup.find_all('img', attrs={'class': 'slide_image'})
    resolution = get_best_resolution(slides_markup)

    # download images from markup array
    dir_tmp = mkdtemp()
    try:
        slides_downloaded = get_slides(slides_markup, resolution, dir_tmp)
        file_output = convert_to_pdf(slides_downloaded, output_path)

        return file_output

    finally:
        rmtree(dir_tmp)

def check_url(url):
    """Check if url is valid and return boolean."""
    is_allowed = False
    allowed_domains = set(['slideshare.net', 'www.slideshare.net', 'es.slideshare.net', 'pt.slideshare.net', 'de.slideshare.net', 'fr.slideshare.net'])

    if ( isinstance(url, str) ):
        url_parsed = urlparse(url)
        for domain in allowed_domains:
            if domain == url_parsed.netloc:
                is_allowed = True

        return is_allowed

    else:
        raise ValueError('URL must be a string.')

def make_dir(directory_path):
    """Try to create directory, raise exception if unsuccessfull. """
    if directory_path != '':
        try:
            os.makedirs(directory_path)
        except OSError:
            if not os.path.isdir(directory_path):
                raise

def get_slide_metadata(_url):
    """Parse url with regex and return author and title."""
    match = search('(?:[^\/]*\/){3}([A-Za-z0-9-_\.]*)(?:\/)([A-Za-z0-9-_\.]*)', _url)
    author = match.group(1)
    title = match.group(2)

    return author, title

def download_image(file_remote, file_local):
    """Download image blob and save with Wand."""
    r = get(file_remote, stream=True)
    if r.status_code == 200:
        # use wand to save file
        with Image(blob=r) as img:
            img.save(filename=file_local)
    else:
        r.raise_for_status

def get_html(url):
    """Get raw html."""
    html = get(url)
    html.raise_for_status()

    return html

def get_best_resolution(slides_markup):
    """Find best resolution available in markup."""
    resolution = None

    if slides_markup[0].has_attr('data-full'):
        resolution = 'data-full'

    elif slides_markup[0].has_attr('data-normal'):
        resolution = 'data-normal'

    else:
        raise Exception('No appropriate resolution found')

    return resolution

def get_slides(slides_markup, resolution, directory):
    """Download images from array to a temporary directory."""
    slides_downloaded = []
    for i, image in enumerate(slides_markup, start=1):
        # form slides data
        file_remote = image[resolution]
        file_local = os.path.join(directory, 'slide-{}.jpg'.format(str(i)))

        try:
            download_image(file_remote, file_local)

        except Exception, e:
            # cleanup and terminate
            rmtree(directory)
            raise Exception('Unable to download image {} to location {}. Error: {}'.format(file_remote, file_local, e))

        else:
            # add to array
            slides_downloaded.append(file_local)

    return slides_downloaded


def convert_to_pdf(slides_downloaded, output_path):
    """Convert images in array to pdf using output_path."""
    with Image() as wand:
        for image_path in slides_downloaded:
            with Image(filename=image_path) as page:
                wand.sequence.append(page)

        wand.save(filename=output_path)

        return output_path

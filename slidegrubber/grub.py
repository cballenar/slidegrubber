#!/usr/bin/env python
import os
import logging
from re import search
from shutil import rmtree
from requests import get
from tempfile import mkdtemp
from wand.image import Image
from bs4 import BeautifulSoup
from urlparse import urlparse
# from socket import setdefaulttimeout

class SlideGrubber(object):
    OUTPUT_FORMAT = '.pdf'
    url = None
    soup = None
    title = None
    author = None
    output_path = None
    slides_markup = None

    def __init__(self, url):
        logging.info('Initializing with %s', url)

        # socket.setdefaulttimeout(20) # used to avoid extra long hangs. Is this necessary?

        # check url validity
        if not self.check_url(url):
            raise ValueError('The URL requested is not valid.')

        self.url = url

        # get html and soup it up
        html = self.get_html(url)
        self.soup = BeautifulSoup(html.text, 'html.parser')

        # get slide title and author from soup
        self.title = self.get_title(self.soup)
        self.author = self.get_author(self.soup)

        # get array of slides img tags
        self.slides_markup = self.get_slides_markup(self.soup)

        # return info upon success
        print 'Your presentation {} by {} is ready for processing.'.format(self.title, self.author)


    def grub(self, output_path=None, slides_markup=None):
        """Perform complete grub operation."""
        logging.info('Checking grub() arguments')

        # check if slides_markup is available, otherwise use entire slides_markup by default
        if (slides_markup == None):
            slides_markup = self.slides_markup

        # check for an output_path and build if incomplete or not available
        self.set_output(output_path)

        # get best resolution available in array
        resolution = self.get_best_resolution(slides_markup)

        logging.info('Grubbing %s slides to %s', len(slides_markup), output_path)

        # download images from markup array
        dir_tmp = mkdtemp()
        try:
            slides_downloaded = self.get_slides(slides_markup, resolution, dir_tmp)
            file_output = self.convert_to_pdf(slides_downloaded, self.output_path)

            return file_output

        finally:
            rmtree(dir_tmp)

    def check_url(self, url):
        """Check if url is valid and return boolean."""
        logging.info('Checking url %s', url)

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

    def make_dir(self, directory_path):
        """Try to create directory, raise exception if unsuccessfull. """
        logging.info('Making directory %s', directory_path)

        if directory_path != '':
            try:
                os.makedirs(directory_path)
            except OSError:
                if not os.path.isdir(directory_path):
                    raise

    def get_filename(self):
        """Parse url with regex and return the formatted filename."""
        logging.info('Getting filename from url')

        match = search('(?:[^\/]*\/){3}([A-Za-z0-9-_\.]*)(?:\/)([A-Za-z0-9-_\.]*)', self.url)
        filename = '{}-by-{}'.format(match.group(2), match.group(1))

        return filename

    def set_output(self, output_path):
        """Sets output_path. It takes a path string as an argument and completes it if necessary."""
        logging.info('Checking and setting correct output based on %s', output_path)

        # if no path is supplied set to empty string
        if output_path == None:
            output_path = ''

        # split for testing
        output_dir, output_file = os.path.split(output_path)

        # if no output directory, use current one
        if output_dir == '':
            output_dir = os.getcwd()

        logging.info('Final output directory is %s', output_dir)

        # if no output filename, build from url
        if output_file == '':
            output_file = self.get_filename()

        # check filename for correct format
        if output_file[-4:] != self.OUTPUT_FORMAT:
            output_file = '{}{}'.format(output_file, self.OUTPUT_FORMAT)

        logging.info('Final output file is %s', output_file)

        # create directory
        self.make_dir(output_dir)

        # rebuild output path
        output_path = os.path.join(output_dir, output_file)

        logging.info('Final output path is %s', output_path)

        # set output properties
        self.output_path = output_path

    def download_image(self, file_remote, file_local):
        """Download image blob and save with Wand."""
        logging.info('Downloading image %s to %s', file_remote, file_local)

        r = get(file_remote, stream=True)
        if r.status_code == 200:
            # use wand to save file
            with Image(blob=r) as img:
                img.save(filename=file_local)
        else:
            r.raise_for_status

    def get_html(self, url):
        """Get raw html."""
        logging.info('Getting html from %s', url)

        html = get(url)
        html.raise_for_status()

        return html

    def get_title(self, soup):
        """Inspect HTML soup for the title of the presentation."""
        title = self.soup.head.title.string[0:59]

        return title

    def get_author(self, soup):
        """Inspect HTML soup for the author of the presentation."""
        author = soup.find(attrs={'class':'slideshow-info'}).find('h2').find(attrs={'itemprop':'name'}).string

        return author

    def get_slides_markup(self, soup):
        """Inspect HTML soup for the markup of each slide and append to list."""
        slides_markup = soup.find_all('img', attrs={'class': 'slide_image'})

        if not slides_markup:
            raise Exception('Dynamic slides are not supported')

        return slides_markup

    def get_best_resolution(self, slides_markup):
        """Find best resolution available in markup."""
        logging.info('Getting best resolution available')

        resolution = None

        if slides_markup[0].has_attr('data-full'):
            resolution = 'data-full'

        elif slides_markup[0].has_attr('data-normal'):
            resolution = 'data-normal'

        else:
            raise Exception('No appropriate resolution found')

        logging.info('The best resolution available is %s', resolution)

        return resolution

    def get_slides(self, slides_markup, resolution, directory):
        """Download images from array to a temporary directory."""
        logging.info('Getting slides from markup using resolution %s to %s', resolution, directory)

        slides_downloaded = []
        for i, image in enumerate(slides_markup, start=1):
            # form slides data
            file_remote = image[resolution]
            file_local = os.path.join(directory, 'slide-{}.jpg'.format(str(i)))

            try:
                self.download_image(file_remote, file_local)

            except Exception, e:
                # cleanup and terminate
                rmtree(directory)
                raise Exception('Unable to download image {} to location {}. Error: {}'.format(file_remote, file_local, e))

            else:
                # add to array
                slides_downloaded.append(file_local)

        return slides_downloaded


    def convert_to_pdf(self, slides_downloaded, output_path):
        """Convert images in array to pdf using output_path."""
        logging.info('Converting %s slides to pdf and saving to %s', len(slides_downloaded), output_path)

        with Image() as wand:
            for image_path in slides_downloaded:
                with Image(filename=image_path) as page:
                    wand.sequence.append(page)

            wand.save(filename=output_path)

            return output_path

SlideGrubber
============

Slidegrubber is a python package that can download SlideShare presentations as PDF files.
It uses the power of BeautifulSoup_, ImageMagick_ (through Wand_), and Requests_.


Requirements
------------
You will need ImageMagick installed on your system to be able to do the image-to-pdf conversion.

.. code-block:: console

    $ apt-get install imagemagick

Install
-------
Run the standard setup.py

.. code-block:: console

    $ python setup.py install

Usage
-----
You can pass the url to initialize the class and then call grub() to download the presentation to a pdf file.

.. code-block:: console

    >>> from slidegrubber import SlideGrubber
    >>> s = SlideGrubber('http://www.slideshare.net/author/my-slide')
    Your presentation My Slide by author is ready for processing.
    >>> s.grub()
    '/current_working_directory/my-slide-by-author.pdf'

If no filename or path is specified the presentation will be downloaded to the current working directory using the url to build the name. But you can also specify the output path, like so:

.. code-block:: console

    >>> s.grub('/my_local_path/my_slide.pdf')
    '/my_local_path/my_slide.pdf'

You can get additional information such as the title, author, and processed output path, directory, and filename after the presentation has been downloaded:

.. code-block:: console

    >>> s.title
    u'My Slide'

    >>> s.author
    u'The Author'

    >>> s.output_dir
    u'/current_working_directory/'

    >>> s.output_filename
    u'my-slide-by-author.pdf'

    >>> s.output_path
    u'/current_working_directory/my-slide-by-author.pdf'

The slides markup can also be accessed as a property and you can pass the images markup to grub() as a second argument to specify what images to convert to pdf. This is helpful if you only need a fraction of the images but it requires more work.

.. code-block:: console

    >>> # get entire markup
    >>> markup = s.slides_markup
    (u'<img ...>', u'<img ...>', ...)

    >>> # grab first five slides
    >>> s.grub('', markup[:5])
    u'/current_working_directory/my-slide-by-author.pdf'


.. _BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/
.. _ImageMagick: http://www.imagemagick.org/
.. _Wand: http://wand-py.org/
.. _Requests: http://docs.python-requests.org/

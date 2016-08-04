SlideGrubber
============

Slidegrubber is a python package that can download SlideShare presentations as PDF files.
It uses the power of BeautifulSoup_, ImageMagick_ (through Wand_), and Requests_.


Requirements
------------
You will need ImageMagick installed on your system to be able to do the image to pdf conversion.

.. code-block:: console
    $ apt-get install imagemagick


Usage
-----
You can simply pass the url as the only argument and it will download the pdf to the current working directory:

.. code-block:: console
    >>> from slidegrubber import grub
    >>> grub('http://www.slideshare.net/author/my-slide')
    '/current_working_directory/my_slide-by-author.pdf'

Or you can specify where to download it:

.. code-block:: console
    >>> from slidegrubber import grub
    >>> grub('http://www.slideshare.net/author/my-slide', '/my_local_path/my_slide.pdf')
    '/my_local_path/my_slide.pdf'

.. _BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/
.. _ImageMagick: http://www.imagemagick.org/
.. _Wand: http://wand-py.org/
.. _Requests: http://docs.python-requests.org/

.. role:: raw-html-m2r(raw)
   :format: html


pymodi
======

:raw-html-m2r:`<img src="https://www.gresswell.co.uk/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/L/3/L308260_MODI_logo_LFC.jpg" width="500" height="150">`

----



Easy😆 and fast💨 MODI Python API package.


* Free software: MIT license
* Documentation: https://pymodi.readthedocs.io.

Features
--------

* Connect to the MODI network module and control input & output
  modules.
* List serial ports of MODI network modules.
* Turn on or off the PnP mode of MODI modules.
* Get the position information of each modules.

Contribution Guidelines
-----------------------

We appreciate all contributions. If you are planning to report bugs, please do so at https://github.com/LUXROBO/pyMODI/issues. Feel free to fork our repository to your local environment, and please send us feedback by filing an issue.

If you want to contribute to pymodi, be sure to review the contribution guidelines. This project adheres to pymodi's code of conduct. By participating, you are expected to uphold this code.


.. image:: https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg
   :target: CODE_OF_CONDUCT.md
   :alt: Contributor Covenant


Quickstart
----------

Install the latest pyMODI if you haven\'t installed it yet:

.. code-block::

   pip install -U pymodi --user


Import [modi]{.title-ref} package and create [MODI]{.title-ref}
instance:

.. code-block::

   import modi
   bundle = modi.MODI(nb_modules=1)


List connected modules:

.. code-block::

   bundle.modules


List connected LED modules and pick the first one:

.. code-block::

   bundle.leds # List.
   bundle.leds[0] # Pick.


Let\'s blink the LED\'s light 5 times:

.. code-block::

   import time

   led = bundle.leds[0]

   for _ in range(5):
       led.set_on()
       time.sleep(1)
       led.set_off()
       time.sleep(1)

matcher.py: Sortable Coding Challenge entry
===

Usage
---
Clone this git repo and change to the same directory. Run `python matcher.py`. 


By default the script will use the data files in the `data` directory, the products and listings provided on the [Coding Challenge](http://sortable.com/blog/coding-challenge/) page.

To pass in different product and listing files, use the following command line options:  


    -p FILE, --products=FILE
                        Products input file
    -l FILE, --listings=FILE
                        Listings input file

The script will write the file **results.txt** in the working directory, which has a serialized JSON object for each product and matching listings, separated by newlines.

Contact
---
Perry Trinier ( perrytrinier@gmail.com )
http://ca.linkedin.com/in/perrytrinier

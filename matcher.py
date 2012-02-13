import codecs
import copy
import json
from optparse import OptionParser
import re
import sys

DEFAULT_PRODUCTS_FILE = 'data/products.txt'
DEFAULT_LISTINGS_FILE = 'data/listings.txt'

def get_input_files():
    """ Parse command line arguments to determine input files to use or set to defaults if none are provided. """
    parser = OptionParser()
    parser.add_option("-p", "--products", dest="products_file",
                      help="Products input file", metavar="FILE")
    parser.add_option("-l", "--listings", dest="listings_file",
                      help="Listings input file", metavar="FILE")

    (options, args) = parser.parse_args()

    input_files = {}

    input_files["products"] = options.products_file or DEFAULT_PRODUCTS_FILE
    input_files["listings"] = options.listings_file or DEFAULT_LISTINGS_FILE

    return input_files

def jsonfile_to_list(fn):
    """ Given a path, return list of python dicts from a text file formatted with one JSON object per line. """
    try:
        with open(fn, 'r') as f:
            return [ json.loads(line) for line in f ]
    except IOError:
        print 'One or more input files does not exist.'
        sys.exit(1)
    except ValueError:
        print 'No JSON object could be decoded.'
        sys.exit(1)

def regexify_hyphens(str):
    """ Replace spaces or hyphens with a string that can be used as part of a regex. """
    return re.sub('[ -]','[ -]?',str)

def get_unmatched_listings(listings_list):
    """ Return unmatched listings. Helpful for debugging. """
    unmatched = [listing for listing in listings_list
                    if not "matched" in listing.keys()]

    return unmatched

def get_product_tokens(str_list):
    """ Given a list of list of strings, split each on our regular expression and lowercase. 
    Next, check tokens against an "alphanumeric" regex to split model names like e.g. PL170 into tokens PL and 170. """
    split_re = re.compile("[- _]")
    all_tokens = []

    # split tokens and lowercase them
    for str in str_list:
        tokens = split_re.split(str)
        tokens = map(lambda str: str.lower(),tokens)
        all_tokens = all_tokens + tokens

    # set up alphanumeric regexen
    numfirst_regex = re.compile("^(\d+)(\D+)")
    ltrfirst_regex = re.compile("^(\D+)(\d+)")

    for token in all_tokens:

        try:
            match_obj_numfirst = numfirst_regex.match(token)
            if not match_obj_numfirst == None:
                all_tokens = all_tokens + list(match_obj_numfirst.groups())

            match_obj_ltrfirst = ltrfirst_regex.match(token)
            if not match_obj_ltrfirst == None:
                all_tokens = all_tokens + list(match_obj_ltrfirst.groups())
        except AttributeError:
            pass

    return unique(all_tokens)

# from http://www.peterbe.com/plog/uniqifiers-benchmark
def unique(seq, idfun=None): 
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result
    
# Main program flow begins
def main(): 
    # Determine input files to use
    input_files = get_input_files()
    print "Opening input files:"
    print "Products: {0}".format(input_files["products"])
    print "Listings: {0}".format(input_files["listings"])

    # Get python lists of our data files
    products_list = jsonfile_to_list(input_files["products"])
    listings_list = jsonfile_to_list(input_files["listings"])

    # Copy original list so the output won't have the extra properties I'm adding to it
    orig_listings_list = copy.deepcopy(listings_list)

    print "Mapping {0} listings to {1} unique products...".format(len(listings_list), len(products_list) )

    # Prepare product data
    all_products = {}
    all_product_tokens = []

    for product in products_list:

        # Create an empty destination list for listings matched to this product
        all_products[product["product_name"]] = []

        # Create regex to match the model
        model_hyphens_fixed = regexify_hyphens(product["model"])
        model_re = r'\b'+model_hyphens_fixed+r'\b'
        product["model_re"] = re.compile(model_re, re.IGNORECASE)

        # Split important product properties into tokens and lowercase the tokens
        product["tokens"] = get_product_tokens([product["product_name"], product["model"], product["manufacturer"]])

        # Save the length to a key for later use
        product["tokens_length"] = len(product["tokens"])

    # Create a title_lower for every listing 
    # so we don't need to call lower() inside the big loop when comparing with tokens
    for listing in listings_list:
        listing["title_lower"] = listing["title"].lower()

    # Matching process starts here
    for listing in listings_list:
        for product in products_list:

            # Check how many tokens for the product are present in the listing title
            matching_tokens = 0
            for token in product["tokens"]:
                if token in listing["title_lower"]:
                    matching_tokens += 1

            # If enough tokens match
            if matching_tokens >= product["tokens_length"] - 2:

                # And the product and listing share a manufacturer
                if (product["manufacturer"].lower() in listing["manufacturer"].lower() or \
                listing["manufacturer"].lower() in product["manufacturer"].lower() ):

                    # Test model regex against the title
                    model_re_match = product["model_re"].search(listing["title_lower"])

                    if not model_re_match == None:

                        # If all conditions are satisfied, add listing to results for this product
                        # Note: appending the original listing, not the one we've been working with
                        listing["matched"] = True
                        the_orig_listing = orig_listings_list[listings_list.index(listing)]
                        all_products[product["product_name"]].append(the_orig_listing)

    # using codecs module to write file as utf-8
    with codecs.open('results.txt', 'w+', 'utf-8') as outputfile:
        for product in all_products:
            listings = all_products[product]
            results_dict = {}
            results_dict["product_name"] = product
            results_dict["listings"] = listings
            json_str = json.dumps(results_dict,ensure_ascii=False)
            outputfile.write(json_str+"\n")

if __name__ == '__main__':
    main()

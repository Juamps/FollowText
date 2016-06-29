

import flickrapi

## GLOBAL VARIABLES
PER_PAGE = 1  # 1-250; documentation says 500 but tried it and only get up to 250 per page
KEYS = {}
FLICKR = []
HEADERS = ["id", "title", "description", "date taken", "photopage", "photostatic"]
all_photos = []

class Flickr_connector:

    def __init__(self, filepath):
        '''
        :param filepath: path to keys file
        :return:
        '''
        ## Read api keys from file
        self.keys = {}
        with open(filepath, "rb") as f:
            lines = f.readlines()
        for line in lines:
            l = line.split(',')
            self.keys[l[0].strip()] = l[1].strip()

        self.flickr = flickrapi.FlickrAPI(self.keys['flickr_key'], self.keys['flickr_secret'])
        if self.flickr:
            self.flickr.authenticate_via_browser(perms='read')

    def fetch_photo_page(self, tags, per_page=PER_PAGE):


        photo_page = self.flickr.photos.search(tags=tags, accuracy=11,
                                      per_page=per_page, page=1,  # default page = 1
                                      extras='original_format')[0]

        return photo_page

    def fetch_photo(self, tags):
        '''
        :param tags: tag to fetch image of
        '''

        photo = self.flickr.photos.search(tags=tags, accuracy=11,
                                      per_page=PER_PAGE, page=1,  # default page = 1
                                      extras='original_format')[0][0]

        photo_id = photo.get('id')
        ## get available sizes
        sizes = self.flickr.photos.getSizes(photo_id=photo_id)[0]
        ## get largest size url
        root = sizes[-1]
        static_url = root.get("source")

        # url = root.get("url")
        # print static_url, url

        return static_url




if __name__ == "__main__":
    pass
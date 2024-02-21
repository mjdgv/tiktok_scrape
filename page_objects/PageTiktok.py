from seleniumbase import Driver
#from selenium import webdriver
from selenium.webdriver.common.by import By # contains operators for the type of search we want to do
import time
from seleniumbase import BaseCase
from random import randint
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import html
import re
import numpy as np
import csv
from datetime import datetime
import os.path

"""
1 batch = the number of posts available on page before scrolling down and loading more.
"""

class PageTiktok(BaseCase): #inherit BaseCase
    predefined_hashtag_list = ["viral","foryou"]
    chromebrowser = Driver(uc=True)
    actions = ActionChains(chromebrowser)
    current_batch = []
    len_all_posts = None
    all_videos_on_page = []
    current_time = datetime.now().strftime("%m-%d-%H-%M")
    language_ops = ['https://www.tiktok.com/en/', 'https://www.tiktok.com/es/', 'https://www.tiktok.com/fr/',
                 'https://www.tiktok.com/foryou?lang=de-DE', 'https://www.tiktok.com/ar/', 'https://www.tiktok.com/foryou?lang=hi-IN']
    
    def fetch_tiktok(self, language_index):
        """
        Opens tiktok, provide time for manual log in, fills in the current_batch with the posts preloaded on screen.
        """ 
        tiktok_url = self.language_ops[language_index]
        self.chromebrowser.uc_open_with_reconnect(tiktok_url,reconnect_time=5) #link to login page
        time.sleep(40)

        #initialize values
        try:
            self.current_batch = self.chromebrowser.find_elements(By.XPATH, '//*[@class="css-14bp9b0-DivItemContainer etvrc4k0"]')
            self.all_videos_on_page = self.current_batch
            self.len_all_posts = len(self.all_videos_on_page)
        except StaleElementReferenceException:
            self.fetch_tiktok(language_index)

    def info_videos(self, videoList):
        '''
        When given a list of video divs, return a summary of each video
        [{'index': 1, 'video': web_element, 'hashtag': [], 'author': 'author_name', 'likes': 123}, ...]
        '''
        summary = []
        for index, video in enumerate(videoList):
            author = self.get_author(video)
            likes = self.get_stats(video,0)
            comments = self.get_stats(video,1)
            shares = self.get_stats(video,2)
            saves = self.get_stats(video,3)
            hashtag = self.get_hashtag(video)
            music = self.get_music(video)
            batch_number = self.batch_num
            summary.append({'batch': batch_number, 'index': index, 'music': music, 'video': video, 'hashtag': hashtag, 'author': author, 'likes': likes, 'comments': comments, 'shares':shares, 'saves': saves})

        return summary
        

    def get_author(self, video):
        try:
            author_element = video.find_element(By.XPATH, ".//*[@class='css-1k5oywg-H3AuthorTitle emt6k1z0']")
            return author_element.text if author_element else None
        except NoSuchElementException:
            print("Author element not found.")
            return None

    def get_stats(self, video, target):
        try:
            like_button = video.find_elements(By.XPATH, ".//*[@class='css-1ok4pbl-ButtonActionItem e1hk3hf90']")[target]
            like_text = like_button.get_attribute('aria-label')
            
            # Extract numerical value using regex
            match = re.search(r'(\d+\.\d+|\d+)([KM])?', like_text)
            if match:
                # Check if suffix (K or M) is present
                if match.group(2) == 'K':
                    likes = float(match.group(1)) * 1000  # Convert K to actual number
                elif match.group(2) == 'M':
                    likes = float(match.group(1)) * 1000000  # Convert M to actual number
                else:
                    likes = float(match.group(1))
                return int(likes)
            else:
                return 0

        except (NoSuchElementException, ValueError):
            print(f"Unable to retrieve the number of target:{target}")
            return -1


    def get_hashtag(self, video):
        try:
            hashtag_list = video.find_elements(By.XPATH, './/*[@class="ejg0rhn6 css-g8ml1x-StyledLink-StyledCommonLink er1vbsz0"]')
            if hashtag_list:
                return [hashtag.get_attribute('href').split('/')[-1] for hashtag in hashtag_list]
            else:
                return []
        except NoSuchElementException:
            print("Hashtag element not found.")
            return []
        
    def get_music(self, video):
        """
        """
        try:
            music_info = video.find_element(By.XPATH, ".//*[@class='css-pvx3oa-DivMusicText epjbyn3']")
            music_text = music_info.text if music_info else None

            if music_text:
                return music_text
            else:
                return None
        except (NoSuchElementException, ValueError):
            print("Unable to retrieve the number of likes")
            return -1
        
    def login(self):
        """
        not used. Manually log in instead, have to close the 2 popups on the bottom right
        """
        # click "use phone/number/email" on login page
        use_email = self.chromebrowser.find_element(By.XPATH, "/html/body/div[5]/div[3]/div/div/div/div[1]/div/div/div[1]/div[2]/div[2]")
        use_email.click()
        # click "login with email or username"
        self.chromebrowser.find_element(By.XPATH, "/html/body/div[5]/div[3]/div/div/div/div[1]/div[2]/form/div[1]/a").click()
        time.sleep(1)
        input_username = self.chromebrowser.find_element(By.XPATH, "/html/body/div[5]/div[3]/div/div/div/div[1]/div[2]/form/div[1]/input")
        input_password = self.chromebrowser.find_element(By.XPATH, "/html/body/div[5]/div[3]/div/div/div/div[1]/div[2]/form/div[2]/div/input")
        input_username.send_keys(self.email)
        input_password.send_keys(self.password)
        time.sleep(3)
        login = self.chromebrowser.find_element(By.XPATH, "/html/body/div[5]/div[3]/div/div/div/div[1]/div[2]/form/button")
        login.click()
    
    def like_video(self, video):
        """
        returns if the video was successfully liked
        """
        like_successful = False
        try:
            like_button = video.find_elements(By.XPATH, ".//*[@class='css-1ok4pbl-ButtonActionItem e1hk3hf90']")[0]
            self.chromebrowser.execute_script("arguments[0].click();", like_button)
            like_successful = True
            print(f"Clicked button {like_button.get_attribute('aria-label')} using JavaScript")
            time.sleep(1)
        except ElementClickInterceptedException:
            print(f"ElementClickInterceptedException: Could not click the button")
            pass
        return like_successful
    
    def flip(self, prob):
        """
        Return True with probability prob, and False otherwise

        Args:
        prob: a float from 0 to 1, the probability of returning True

        Return:
        True with probability prob, False with probability (1-prob)
        """
        return np.random.random() < prob

    def update_batch(self):
        """
        updates batch by scrolling to the bottom 
        """
        current_batch_exists = False

        self.actions.move_to_element(self.all_videos_on_page[-1]).perform()
        time.sleep(5)
        old_batch = self.current_batch
        old_all_videos = self.all_videos_on_page
        print(f"***old batch:{self.info_videos(old_batch)}\n")
        print(f"\n***length of old batch: {len(old_batch)}\n")

        #print(f"\n***old all videos on page: {self.info_videos(old_all_videos)}")
        print(f"\n***length of old all videos on page:{len(old_all_videos)}")

        self.current_batch = set(old_all_videos) ^ set(self.chromebrowser.find_elements(By.XPATH, '//*[@class="css-14bp9b0-DivItemContainer etvrc4k0"]'))
        print(f"\nIs there no overlap between old batch and new batch?:{self.validate_no_overlapping_post(old_batch, self.current_batch)}")
        
        self.all_videos_on_page = self.chromebrowser.find_elements(By.XPATH, '//*[@class="css-14bp9b0-DivItemContainer etvrc4k0"]')
        #print(f"\n***new all videos on page: {self.info_videos(self.all_videos_on_page)}")
        print(f"\n***length of new all videos on page:{len(self.all_videos_on_page)}")

        if self.current_batch: #if new videos were loaded
            print(f"\n***new batch: {self.info_videos(self.current_batch)}")
            print(f"\n***length of new batch: {len(self.current_batch)}\n")
            current_batch_exists = True
        else:
            print("\n!!!!no new posts were added!!!!\n")
        
        return current_batch_exists


    def validate_no_overlapping_post(self, oldbatch, newbatch):
        ''''
        validates that the the oldbatch and the new batch (videolists) does not overlap
        '''
        return (not(set(oldbatch) & set(newbatch)))
                
    def iterate_through_batches_random(self, batches=5):
        """
        Like posts in current batch after updating randomly, then move on to the next batch
        """
        self.batch_num = 0
        while batches > 0:
            print(f"\n****BATCH #{6-batches}\n")
            batches -= 1
            self.batch_num += 1
            current_batch_info = self.info_videos(self.current_batch)
            time.sleep(5)

            # Uncomment this if want data from random liking
            current_batch_info = self.info_videos(self.current_batch)
            self.write_to_csv(current_batch_info, "random_data_all_videos.csv")
            self.update_batch()

    def write_to_csv(self, data, filename):
        """
        Write data to a CSV file
        """

        csv_file_path = f"./data/{self.current_time}_{filename}"

        file_exists = os.path.isfile(csv_file_path) # checks if file exists already
        
        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['batch', 'index', 'music', 'hashtag', 'author', 'likes','comments','shares','saves']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader() #writes header only once

            for video_info in data:
                writer.writerow({
                    'batch': video_info['batch'], 
                    'index': video_info['index'],
                    'music': video_info['music'],
                    #'video': video_info['video'],
                    'hashtag': ', '.join(video_info['hashtag']),  # Convert list to comma-separated string
                    'author': video_info['author'],
                    'likes': video_info['likes'],
                    'comments': video_info['comments'],
                    'shares': video_info['shares'],
                    'saves': video_info['saves']
                })
  
    


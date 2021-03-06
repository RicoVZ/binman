import os.path
import shutil
import logging

from building.BinaryInfo import BinaryInfo
from config.Config import Config
from data.DbManager import DbManager

class BuildRepository:
    
    def __init__(self):

        if not os.path.exists(Config.samples_dir):
            os.mkdir(Config.samples_dir)
        if not os.path.exists(Config.binaries_dir):
            os.mkdir(Config.binaries_dir)

    def add_all_samples(self):
        
        files = os.listdir(Config.samples_dir)
        dbm   = DbManager()
        
        dbm.open_connection()
        
        for file in files:
            if os.path.isfile(Config.samples_dir + "//" + file):
                b_info = BinaryInfo(Config.samples_dir + "//" + file)
                
                if not dbm.binary_info_exists(b_info):
                    logging.info("Inserting " + b_info.get_sha256())
                    if dbm.save_binary_info(b_info):
                        shutil.copy(Config.samples_dir + "//" + file, Config.binaries_dir + "//" + b_info.get_sha256())

        dbm.close_connection()
    
    def add_single_binary(self, b_info):
        
        success = False
        
        dbm = DbManager()
        dbm.open_connection()
        
        if not dbm.binary_info_exists(b_info):
            if dbm.save_binary_info(b_info):
                success = True
                
        dbm.close_connection()
        
        return success

    def check_db_missing_info(self, fix=False):

        files  = os.listdir(Config.binaries_dir)
        dbm    = DbManager()
        errors = 0

        dbm.open_connection()

        for file in files:
            b_info = BinaryInfo(Config.binaries_dir + "//" + file)
            if not dbm.binary_info_exists(b_info):
                logging.warn("No info found on " + b_info.get_sha256())
                errors += 1

                if fix:
                    dbm.save_binary_info(b_info)
                    if not os.path.isfile(Config.binaries_dir + "//" + b_info.get_sha256()):
                        shutil.copy(Config.binaries_dir + "//" + file, Config.binaries_dir + "//" + b_info.get_sha256())
                    logging.info("Added info to database")

        if errors < 1:
            logging.info("No missing binary info in database")

        dbm.close_connection()

    def check_missing_binaries(self, fix=False):

        files  = os.listdir(Config.binaries_dir)
        dbm    = DbManager()
        errors = 0

        dbm.open_connection()

        all_names = dbm.get_all_file_names()

        for name in all_names:
            
            if not name[0] in files:
                logging.warn("Missing binary: " + name[0])
                errors += 1
                
                if fix:
                    dbm.remove_file_info(name[0])
                    logging.info("Remove file info from database")

        if errors < 1:
            logging.info("No missing binaries")

        dbm.close_connection()
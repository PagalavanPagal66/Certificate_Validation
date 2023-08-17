import os
import cv2
import datetime
import sqlite3
import hashlib
from PIL import Image
from PIL import ImageChops
import streamlit as st
from streamlit_option_menu import option_menu

hashconn = sqlite3.connect('Hash.db')
hashcursor = hashconn.cursor()

def image_to_text(path):
    with open(path,'rb') as file:
        photo = file.read()
    return photo

class Block:
    def __init__(self,data,prev_hash):
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        sha = hashlib.sha256()
        sha.update(self.data.encode('utf-8'))
        return sha.hexdigest()

class BlockChain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block("Genesis Block","0")

    def add_block(self,data):
        prev_block = self.chain[-1]
        new_block = Block(data, prev_block.hash)
        self.chain.append(new_block)

def create_hash_table():
    hashcursor.execute('CREATE TABLE IF NOT EXISTS FINAL_HASH (username TEXT ,domain TEXT, hash TEXT, image BLOB);')
    hashconn.commit()

create_hash_table()
print('TABLE CREATED')

def add_certificate(username, domain, hash, image):
    hashcursor.execute('INSERT INTO FINAL_HASH (username,domain,hash,image) VALUES (?,?,?,?)', (username, domain,hash,image))
    hashconn.commit()

def image_repeat(image):
    hashcursor.execute('SELECT * FROM FINAL_HASH WHERE image = (?)',(image,))
    return len(hashcursor.fetchall())

def view_all_users():
    hashcursor.execute('SELECT * FROM FINAL_HASH')
    data = hashcursor.fetchall()
    return data

blockchain = BlockChain()
print("BLOCK CHAIN ----------------------------------------------------")
values = view_all_users()
print(len(values))

for iter in values:
    blockchain.add_block(str(iter[3]))

def generate_certificate(name,domain,Date):
    certificate_template_image = cv2.imread("C:\\Users\\pagal\\OneDrive\\Desktop\\Certificate_Template.jpg")
    cv2.putText(certificate_template_image, name, (655, 655), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 5, cv2.LINE_AA)
    cv2.putText(certificate_template_image, domain, (950, 835), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 255), 2, cv2.LINE_AA)
    cv2.putText(certificate_template_image, str(Date), (345, 1200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2,cv2.LINE_AA)
    certificate_path = "C:\\Users\\pagal\\PycharmProjects\\TEXT\\CPGPT\\Testing\\generated-certificates/{}.jpg".format(name)
    cv2.imwrite(certificate_path, certificate_template_image)
    print("Processing {} ".format(name))
    if image_repeat(str(image_to_text(certificate_path)))==0:
        print("NEWLY ADDED")
        st.success("NEWLY ADDED")
        values = view_all_users()
        print(len(values))
        for iter in values:
            blockchain.add_block(str(iter[3]))
        add_certificate(name,domain,str(blockchain.chain[-1].hash), image_to_text(certificate_path))
        blockchain.add_block(str(image_to_text(certificate_path)))
    else:
        print("ALREADY ADDED")
        st.success("ALREADY ADDED")
    return certificate_path


def is_valid_certificate(binary_data):
    for block in blockchain.chain:
        print(block.hash)
        print(block.prev_hash)
        if(block.data == str(binary_data)):
            return 'FOUND'
    return 'NOT FOUND'

selected = option_menu(
    menu_title= None,
    options = ['ADD','VERIFY'],
    icons = ['house','book'],
    menu_icon = "cast",
    default_index = 0,
    orientation = "horizontal"
)

@st.cache_data
def load_image(image_file):
    img = Image.open(image_file)
    return img

def body():
    if(selected == 'ADD'):
        st.subheader("Create a Block chain verified certificate by providing the details")
        Name = st.text_input("NAME : ")
        Domain = st.text_input("DOMAIN : ")
        Date = st.date_input("DATE : ")
        if(st.button("SUBMIT")):
            st.image(load_image(generate_certificate(Name,Domain,Date)))
    if(selected=='VERIFY'):
        st.title('Upload images')
        uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.read()
            st.write("filename:", uploaded_file.name)
            st.success("IMAGE UPLOADED SUCCESSFULLY")
            st.write(is_valid_certificate(bytes_data))

if __name__ == '__main__':
    body()
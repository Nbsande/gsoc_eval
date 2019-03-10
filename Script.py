import h5py 
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import datetime
import pytz

f=h5py.File("1541962108935000000_167_838.h5",'r')

#The data to be used in the csv file will be added to the csvTemplate variable
csvTemplate=[['ObjectType','Address','Name','Size','Shape','DataType']]

def DatasetCheck(name, node):
    """ This function takes the '/' separated address of an item in the 
    hdf file and the item itself as parameters. If the item is a Dataset it appends
    the current item's address, name, size, shape and the type of data it contains 
    to the variable csvTemplate"""
    
    global csvTemplate    
    
    if isinstance(node, h5py.Dataset):
        out=['Dataset']
        DataSetPathList=name.split('/')
        ParentGroup=f
        #Get the parent group of the current dataset
        for n in range(len(DataSetPathList)-1):
            ParentGroup=ParentGroup[DataSetPathList[n]]
        
        out.append("/".join(DataSetPathList[:-1]))              #appends the '/' separated address of the dataset
        out.append(DataSetPathList[-1])                         #appends the name of the dataset
        out.append(ParentGroup[DataSetPathList[-1]].size)       #appends the number of elements in the dataset
        out.append(str(ParentGroup[DataSetPathList[-1]].shape)) #appends the shape of the dataset
        
        #h5py raises TypeError when tryin to open certain datasets containing the H5T_NATIVE_B8 datatype  
        try:   
            out.append(ParentGroup[DataSetPathList[-1]].dtype)
        except TypeError:
            out.append("H5T_NATIVE_B8")
        csvTemplate.append(out)  #adds the out array to csvTemplate
    
    else:
        if isinstance(node,h5py.Group):
            out=['Group']
            GroupPathList=name.split('/')
            out=["Group","/".join(GroupPathList[:-1]),GroupPathList[-1],'n/a','n/a','n/a']
            csvTemplate.append(out)
        

#Making the CSV file:

#visititems() recursively gets every item(i.e group, dataset etc) and its address in the hdf file
#and passes it to a specified callable function
f.visititems(DatasetCheck)    
with open('ScriptOutput.csv','w') as h:
    for row in csvTemplate:
        rowstring=[]
        for item in row:
            rowstring.append(str(item))
        h.write(",".join(rowstring)+"\n")


#Plotting the Image:
imgHt=np.array(f['AwakeEventData']['XMPP-STREAK']['StreakImage'].get('streakImageHeight'))[0]
imgWdth=np.array(f['AwakeEventData']['XMPP-STREAK']['StreakImage'].get('streakImageWidth'))[0]
img=np.array(f['AwakeEventData']['XMPP-STREAK']['StreakImage'].get('streakImageData'))
img=medfilt(np.reshape(img,(imgHt,imgWdth)))
plt.imshow(img)
plt.savefig('XMPP-STREAK-Image.png')


#Creating the Datetime objects:
timestamp=round(1541962108935000000/(10**(9)))
date_str = datetime.datetime.fromtimestamp(timestamp)
datetime_obj_UTC = datetime.datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S")
datetime_obj_CERN = datetime_obj_UTC.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Zurich'))

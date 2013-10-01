# -*- coding: cp1252 -*-
import pickle
import numpy
from time import strftime
import phynx
import os
import asciidata



def ksort(d, func = None):
    keys = d.keys()
    keys.sort(func)
    return keys



class scribe(object):
    def __init__(self,target,start_number=0):
        self.target = target
        self.scan_number = start_number

    def write(self,data):
        pass

    def flush(self):
        pass

    def new_scan(self):
        self.scan_number+=1


    
class pkl_scribe(scribe):
    def __init__(self,target,start_number=0):
        super(pkl_scribe,self).__init__(target,start_number=start_number)


        self.data = []        
        self.names = []
        self.origins = []
        
        self.protocol = pickle.HIGHEST_PROTOCOL
        self.min_index_length = 4

    def _get_indx(self):
        indx = str(self.scan_number)
        while len(indx)<self.min_index_length:
            indx = "0"+indx
        return indx
    
    def write(self,datum,name,origin):
        self.data += [datum]
        self.names += [name]
        self.origins += [origin]

    def write_pkl(self):
        try:
            pkl_file=open(self.target+self._get_indx()+".pkl",'wb')
            for i in range(len(self.data)):
                pickle.dump((self.data[i],self.origins[i],self.names[i]),
                            pkl_file,self.protocol)
            # deal with something happening / interfering with data writing
        finally:
            pkl_file.close()


    def new_scan(self):
        self.flush()
        
        self.data = []
        self.names = []
        self.origins = []
        
        self.scan_number += 1

    def flush(self):
        if len(self.data)>0:
            self.write_pkl()
            
    def read_pkl(self,filename):
        data_tuples = []
        try:
            pkl_file = open(filename,'rb')
            while True:
                try:
                    data_tuples += [pickle.load(pkl_file)]
                except (pickle.UnpicklingError, EOFError) :
                    break
        finally:
            pkl_file.close()
            return data_tuples            

##
##test=pkl_scribe('C:\\pkl_scribe_test')
##test.write("TriTraTrullala","Lied","Pippi Langstrumpf")
##test.write("Spam","Sketch","Monty Python")
##test.write("Dead parrot","Sketch","Monty Python")
##test.write("Always look on the bright side","Lied","Monty Python")
##test.flush()
##data=test.read_pkl('C:\\pkl_scribe_test0000.pkl')
##print data
##test.write(1.,"heißt 2","von 3")
##test.new_scan()
##data=test.read_pkl('C:\\pkl_scribe_test0000.pkl')
##print data
##test.write("TriTraTrullala","Lied","Pippi Langstrumpf")
##test.write("Spam","Sketch","Monty Python")
##test.write("Dead parrot","Sketch","Monty Python")
##test.write("Always look on the bright side","Lied","Monty Python")
##test.flush()
##data=test.read_pkl('C:\\pkl_scribe_test0001.pkl')
##print data
##        
##        
    

class HDF5_scribe(scribe):

    
    def __init__(self,target,title,experiment_identifier,HDF5_mapping_file,start_number=0):
        self.target = target
        self.scan_number = start_number
        self.create_NXentry(title,experiment_identifier)

        if HDF5_mapping_file is None:
            HDF5_mapping_file = env.Default_Scribe_HDF5_mapping_file

        self.HDF5_mapping_dict = test.read_dict(HDF5_mapping_file)

        self.cwrite_dict = dict({})
        self.cwrite_chunksize_dict = dict({})


    def write_dict(self,dictname):
        ncols=4
        nrows=0
        for origin in self.HDF5_mapping_dict:
            for name in self.HDF5_mapping_dict[origin]:
                nrows+=len(self.HDF5_mapping_dict[origin][name])
            
        dictfile=asciidata.create(ncols,nrows,delimiter=',',null='None')

        dictfile[0].rename('origin')
        dictfile[1].rename('name')
        dictfile[2].rename('path')
        dictfile[3].rename('dtype')
        
        row=0
        for origin in self.HDF5_mapping_dict:
            for name in self.HDF5_mapping_dict[origin]:
                print origin,name
                for i in range(len(self.HDF5_mapping_dict[origin][name])):
                    dictfile[0][row]=origin
                    dictfile[1][row]=name
                    dictfile[2][row]=self.HDF5_mapping_dict[origin][name][i][0]
                    dictfile[3][row]=self.HDF5_mapping_dict[origin][name][i][-1]
                    row+=1
        dictfile.writeto(dictname,colInfo=True,headComment=True)
                
            
                
    def read_dict(self,dictname): 
        dictfile = asciidata.open(dictname,delimiter=',',null='""')
        new_dict = dict()
        old_origin = ''
        old_name = ''
        name_dict = None
        path_list = []
        
        for row in range(dictfile.nrows):
            origin = dictfile['origin'][row].strip()
            name = dictfile['name'][row].strip()
            path = dictfile['path'][row].strip()
            dtype = dictfile['dtype'][row].strip()
            if dtype == 'None':
                dtype = None
            if origin!=old_origin:
                if not name_dict is None:
                    new_dict.update(dict({old_origin: name_dict}))
                name_dict = dict()
            elif name != old_name:
                name_dict.update(dict({old_name: path_list}))
                path_list = []
            path_list += [[path,dtype]]
            old_origin = origin
            old_name = name
        name_dict.update(dict({name: path_list})) 
        new_dict.update(dict({old_origin: name_dict}))
        return new_dict
        

    
    def write(self,datum,name,origin):
        self.data += [datum]
        self.names += [name]
        self.origins += [origin]
                            
    def flush(self):
        self.write_HDF5()

    def close_NXentry(self):
        try:
            hdf5 = phynx.File(self.target, 'a')
            NXentry = hdf5.require_group(str(self.scan_number))
            NXentry['end_time'] = strftime("%Y-%m-%d %H:%M:%S")
        finally:
            hdf5.close()

    def create_NXentry(self,title,experiment_identifier):

        self.data = []        
        self.names = []
        self.origins = []
        
        try:
            hdf5 = phynx.File(self.target, 'a')
            
            while True:
                try:
                    NXentry = hdf5.require_group(str(self.scan_number), type='NXentry')
                    NXentry['title'] = title
                    NXentry['experiment_identifier'] = experiment_identifier
                    NXentry['start_time'] = strftime("%Y-%m-%d %H:%M:%S")
                    break
                except ValueError:
                    self.scan_number+=1


        finally:
            hdf5.close()

    def new_scan(self,title,experiment_identifier):
        self.close_NXentry()
        self.scan_number+=1
        self.create_NXentry(title,experiment_identifier)
            
    def associate(self,name,origin):
        HDF_path=self.HDF5_mapping_dict[origin][name]
        return HDF_path


    def write_HDF5(self):
        to_do_groups = dict({})
        path_to_data = []
        for i in range(len(self.data)):
            all_paths = self.associate(self.names[i],self.origins[i])
            root_path=''
            for j in range(len(all_paths)-1):
                if j!=len(all_paths)-1:
                    to_do_groups.update(dict({root_path+all_paths[j][0]:all_paths[j][-1]}))
                    root_path+=all_paths[j][0]+'/'                    
            if root_path == '':
                path_to_data+=[path_to_data[-1]]
            else:                
                path_to_data+=[root_path]
            
        path_to_cdata = []
        for origin in self.cwrite_dict:
            for name in self.cwrite_dict[origin]:
                all_paths = self.associate(name,origin)
                root_path=''
                for j in range(len(all_paths)-1):
                    if j!=len(all_paths)-1:
                        to_do_groups.update(dict({root_path+all_paths[j][0]:all_paths[j][-1]}))
                        root_path+=all_paths[j][0]+'/'                    
                path_to_cdata+=[root_path]

        sorted_keys_groups=ksort(to_do_groups)


        
        try:
            hdf5 = phynx.File(self.target, 'a')
            NXentry = hdf5.require_group(str(self.scan_number), type='NXentry')
            print "Creating tree structure"
            for key in sorted_keys_groups:
                print key,
                print to_do_groups[key]
                NXentry.require_group(key,type=to_do_groups[key])

            print "Writing static data"
            for i in range(len(self.data)):
                NXentry[path_to_data[i]].require_dataset(self.names[i],data = self.data[i])

            i=0
            print "Writing scan data"
            for origin in self.cwrite_dict:
                for name in self.cwrite_dict[origin]:
                    print type(self.cwrite_dict[origin][name])
                    NXentry[path_to_cdata[i]].require_dataset(name,data = self.cwrite_dict[origin][name])
                    i+=1
                    
                    
                    
        finally:
            hdf5.close()

            
    def init_cwrite(self,data_shape,data_type,name,origin,chunksize=None):
        if origin not in self.cwrite_dict:
            self.cwrite_dict.update(dict({origin : dict({})}))
            self.cwrite_chunksize_dict.update(dict({origin : dict({})}))
        self.cwrite_dict[origin].update(dict({name: numpy.zeros(data_shape,dtype=data_type)}))
        self.cwrite_chunksize_dict[origin].update(dict({name: chunksize}))
        
    def cwrite(self,data,name,origin,numpy_slice):
        self.cwrite_dict[origin][name][numpy_slice]=data

##if os.path.exists('C:\\scribe_test.h5'):
##    os.remove('C:\\scribe_test.h5')
##test=HDF5_scribe('C:\\scribe_test.h5',"Test","Exp000")
##test.new_scan("Test2","Exp000")
##test.new_scan("Test3","Exp000")
####test.write_dict("C:\\test_dictwriter.txt")
##test.HDF5_mapping_dict = test.read_dict("C:\\test_dictwriter.txt")
####test.write("TriTraTrullala","Lied","Pippi Langstrumpf")
####test.write("Spam","Sketch","Monty Python")
####test.write("Dead parrot","Sketch","Monty Python")
####test.write("Always look on the bright side","Lied","Monty Python")
####test.flush()
####test.write(1.,"heißt 2","von 3")
####test.flush()
##test.write(5,"Vortex #1 sampletime","p06/XIA/exp.01")
##test.init_cwrite((100,100,1024),numpy.float32,"Vortex #1 fluorescence counts","p06/XIA/exp.01")
####test.flush()
##test.cwrite(numpy.random.rand(1024),"Vortex #1 fluorescence counts","p06/XIA/exp.01",numpy.s_[1,1,0:1024])
##test.close_NXentry()
##test.flush()
##        
##        
   

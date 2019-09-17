import os

def convert(path_lab,path_img,cls,lab):
    out_cls = open(cls,'w')
    out_lab = open(lab,'w')
    list_cls = []
    g = os.walk(path_lab)

    ### generate csv file for labels
    for root, _, file_list in g:
        for file_name in file_list:
            label = open(root + file_name, 'r')
            num = int(label.readline())
            for _ in range(num):
                line = label.readline()
                cls_name = line.split()[4]
                if cls_name not in list_cls:
                    list_cls.append(cls_name)
                output = path_img + file_name.replace('.txt','.jpg') + ',' + line.replace('\n','').replace(' ',',')
                out_lab.write(output+'\n')
    

    ### generate csv file for classes                
    for id, name in enumerate(list_cls):
        out_cls.write(name + ',' + str(id) + '\n')

def main():
    path_labels = 'C:/Users/sheny/Documents/GitHub/dr-2019sp/BBOX/Labels/111/'
    path_images = 'C:/Users/sheny/Documents/GitHub/dr-2019sp/BBOX/Images/111/'
    csv_cls = 'classes.csv'
    csv_lab = 'labels.csv'
    convert(path_labels,path_images,csv_cls,csv_lab)

if __name__ == '__main__':
    main()
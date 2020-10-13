from __future__ import print_function, division
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
import time
import copy
import os
# import mb2
from torchvision.models import MobileNetV2
from torch.utils.data import DataLoader


def train_model(model, criterion, optimizer, num_epochs, dset_sizes, dset_loaders):
    for epoch in range(num_epochs):
        print('-' * 35)
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        
        model.train()  # model convert to train state

        running_loss = 0.0
        running_corrects = 0

        counter = 0

        for data in dset_loaders:

            inputs, labels = data
            if torch.cuda.is_available():
                inputs, labels = Variable(inputs.float().cuda()), Variable(labels.long().cuda())
            else:
                inputs, labels = Variable(inputs), Variable(labels)

            optimizer.zero_grad()
            outputs = model(inputs)
            _, preds = torch.max(outputs.data, 1)
                
            loss = criterion(outputs, labels)
            counter += 1

            
            loss.backward()  # find the gradient for the loss
            optimizer.step()  # update model.parameters
            try:
                running_loss += loss.item()
                running_corrects += torch.sum(preds == labels.data)
            except:
                print('unexpected error, could not calculate loss or do a sum.')

        epoch_loss = running_loss / dset_sizes
        print('Loss: {:.4f}'.format(epoch_loss))
             
    return model


DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

epoch = 20
batch_size = 32
num_class = 10

time_a = time.time()
print("-"*35)

print(f"Batch Size  :  {batch_size}")
print(f"Epoch       :  {epoch}")

model_ft: MobileNetV2 = models.mobilenet_v2(pretrained=True)

for param in model_ft.parameters():
    param.requires_grad = False  # replace the last fully-connected layer

model_ft.classifier = nn.Sequential(
                        nn.Linear(1280, 100),
                        nn.ReLU(inplace=True),
                        nn.Linear(100, num_class))


data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224),  # 224
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])}

dsets = datasets.ImageFolder("example/train/", data_transforms['train'])
        
dset_loaders = torch.utils.data.DataLoader(dsets, batch_size=int(batch_size), shuffle=True)
dset_sizes = len(dsets)  # 2000
dset_classes = dsets.classes

criterion = nn.CrossEntropyLoss()  # -(expected value)*(answer)
if torch.cuda.is_available():
    criterion.cuda()
    model_ft.cuda()
optimizer_ft = optim.Adam(model_ft.parameters())

model_ft = train_model(model_ft, criterion, optimizer_ft, epoch, dset_sizes, dset_loaders)

torch.save(model_ft, "example/model/savetest.pth")

time_b = time.time()
print(f"total time:{time_b - time_a}")
print("TRAINING DONE")

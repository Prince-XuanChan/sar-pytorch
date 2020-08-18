'''
This code is to construct backbone network for SAR - with 13 layers of customized ResNet.
'''
import torch
import torch.nn as nn

__all__ = ['basicblock','backbone']
    
class basicblock(nn.Module):
    def __init__(self, depth_in, output_dim, kernel_size, stride):
        super(basicblock, self).__init__()
        self.identity = nn.Identity()
        self.conv_res = nn.Conv2d(depth_in, output_dim, kernel_size=1, stride=1)
        self.conv1 = nn.Conv2d(depth_in, output_dim, kernel_size=kernel_size, stride=stride, padding=1)
        self.conv2 = nn.Conv2d(output_dim, output_dim, kernel_size=kernel_size, stride=stride, padding=1)
        self.relu = nn.ReLU(inplace=True)
        self.depth_in = depth_in
        self.output_dim = output_dim

    def forward(self, x):
        # create shortcut path
        if self.depth_in == self.output_dim:
            residual = self.identity(x)
        else:
            residual = self.conv_res(x)
        out = self.conv1(x)
        out = self.conv2(out)

        out += residual
        out = self.relu(out)

        return out

class backbone(nn.Module):

    def __init__(self, input_dim):
        super(backbone, self).__init__()
        self.conv1 = nn.Conv2d(input_dim, 64, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.maxpool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        # Block 1 starts
        self.basicblock1 = basicblock(128, 256, kernel_size=3, stride=1)
        # Block 1 ends
        self.conv3 = nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1)
        self.maxpool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        # Block 2 starts
        self.basicblock2 = basicblock(256, 256, kernel_size=3, stride=1)
        self.basicblock3 = basicblock(256, 256, kernel_size=3, stride=1)
        # Block 2 ends
        self.conv4 = nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1)
        self.maxpool3 = nn.MaxPool2d(kernel_size=(1,2), stride=(1,2))
        # Block 5 starts
        self.basicblock4 = basicblock(256, 512, kernel_size=3, stride=1)
        self.basicblock5 = basicblock(512, 512, kernel_size=3, stride=1)
        self.basicblock6 = basicblock(512, 512, kernel_size=3, stride=1)
        self.basicblock7 = basicblock(512, 512, kernel_size=3, stride=1)
        self.basicblock8 = basicblock(512, 512, kernel_size=3, stride=1)
        # Block 5 ends
        self.conv5 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        # Block 3 starts
        self.basicblock9 = basicblock(512, 512, kernel_size=3, stride=1)
        self.basicblock10 = basicblock(512, 512, kernel_size=3, stride=1)
        self.basicblock11 = basicblock(512, 512, kernel_size=3, stride=1)
        # Block 3 ends
        self.conv6 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.maxpool1(x)
        x = self.basicblock1(x)
        x = self.conv3(x)
        x = self.maxpool2(x)
        x = self.basicblock2(x)
        x = self.basicblock3(x)
        x = self.conv4(x)
        x = self.maxpool3(x)
        x = self.basicblock4(x)
        x = self.basicblock5(x)
        x = self.basicblock6(x)
        x = self.basicblock7(x)
        x = self.basicblock8(x)
        x = self.conv5(x)
        x = self.basicblock9(x)
        x = self.basicblock10(x)
        x = self.basicblock11(x)
        x = self.conv6(x)

        return x

# unit test
if __name__ == '__main__':

    batch_size = 32
    Height = 48
    Width = 160
    Channel = 3

    input_images = torch.randn(batch_size,Channel,Height,Width)
    model = backbone(Channel)
    output_features = model(input_images)

    print("Input size is:",input_images.shape)
    print("Output feature map size is:",output_features.shape)
# league-of-legends-bot

### Demo Videos
* [Object detection demo](https://drive.google.com/file/d/1Gh4WtFk9ToJuur6n2vqFqkCO9sqrxSoX/view?usp=sharing)
* [LSTM and LSTM+PPO demo](https://drive.google.com/open?id=1pfB3na3cBMGpqV61aJ8TGsxrXeY8EJpf)

### Materials
* [League of Legends Object Detection Images and Labels](https://drive.google.com/open?id=1juBqe6SQbos621ZPfhurQe_5ZLvjaXCW)
* [Trained YOLOv3 model weights](https://drive.google.com/file/d/1cJtTaaeY7xOI8P7C0lJ7kyEco2fsjPgx/view?usp=sharing)
* [YOLOv3 .cfg file](https://drive.google.com/file/d/1juBqe6SQbos621ZPfhurQe_5ZLvjaXCW/view?usp=sharing)
* [YOLOv3 .data file](https://drive.google.com/open?id=1Q1FB6sVb3uAoba6tQ871KapTkRvmyMQF)

### Requirements
* Windows
* Clone [darknet for windows](https://github.com/AlexeyAB/darknet) into current directory
* **CMake >= 3.8** for modern CUDA support: https://cmake.org/download/
* **CUDA 10.0**: https://developer.nvidia.com/cuda-toolkit-archive (on Linux do [Post-installation Actions](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions))
* **OpenCV >= 2.4**: use your preferred package manager (brew, apt), build from source using [vcpkg](https://github.com/Microsoft/vcpkg) or download from [OpenCV official site](https://opencv.org/releases.html) (on Windows set system variable `OpenCV_DIR` = `C:\opencv\build` - where are the `include` and `x64` folders [image](https://user-images.githubusercontent.com/4096485/53249516-5130f480-36c9-11e9-8238-a6e82e48c6f2.png))
* **cuDNN >= 7.0 for CUDA 10.0** https://developer.nvidia.com/rdp/cudnn-archive (on **Linux** copy `cudnn.h`,`libcudnn.so`... as desribed here https://docs.nvidia.com/deeplearning/sdk/cudnn-install/index.html#installlinux-tar , on **Windows** copy `cudnn.h`,`cudnn64_7.dll`, `cudnn64_7.lib` as desribed here https://docs.nvidia.com/deeplearning/sdk/cudnn-install/index.html#installwindows )
* **GPU with CC >= 3.0**: https://en.wikipedia.org/wiki/CUDA#GPUs_supported
* on Linux **GCC or Clang**, on Windows **MSVC 2015/2017/2019** https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community

Compiling on **Windows** by using `Cmake-GUI` as on this [**IMAGE**](https://user-images.githubusercontent.com/4096485/55107892-6becf380-50e3-11e9-9a0a-556a943c429a.png): Configure -> Optional platform for generator (Set: x64) -> Finish -> Generate -> Open Project -> x64 & Release -> Build -> Build solution

Compiling on **Linux** by using command `make` (or alternative way by using command: `cmake . && make` )

### How to compile on Windows (using `vcpkg`)

If you have already installed Visual Studio 2015/2017/2019, CUDA > 10.0, cuDNN > 7.0, OpenCV > 2.4, then compile Darknet by using `C:\Program Files\CMake\bin\cmake-gui.exe` as on this [**IMAGE**](https://user-images.githubusercontent.com/4096485/55107892-6becf380-50e3-11e9-9a0a-556a943c429a.png): Configure -> Optional platform for generator (Set: x64) -> Finish -> Generate -> Open Project -> x64 & Release -> Build -> Build solution

Otherwise, follow these steps:

1. Install or update Visual Studio to at least version 2017, making sure to have it fully patched (run again the installer if not sure to automatically update to latest version). If you need to install from scratch, download VS from here: [Visual Studio Community](http://visualstudio.com)

2. Install CUDA and cuDNN

3. Install `git` and `cmake`. Make sure they are on the Path at least for the current account

4. Install [vcpkg](https://github.com/Microsoft/vcpkg) and try to install a test library to make sure everything is working, for example `vcpkg install opengl`

5. Define an environment variables, `VCPKG_ROOT`, pointing to the install path of `vcpkg`

6. Define another environment variable, with name `VCPKG_DEFAULT_TRIPLET` and value `x64-windows`

7. Open Powershell and type these commands:

```PowerShell
PS \>                  cd $env:VCPKG_ROOT
PS Code\vcpkg>         .\vcpkg install pthreads opencv[ffmpeg] #replace with opencv[cuda,ffmpeg] in case you want to use cuda-accelerated openCV
```

8.  Open Powershell, go to the `darknet` folder and build with the command `.\build.ps1`. If you want to use Visual Studio, you will find two custom solutions created for you by CMake after the build, one in `build_win_debug` and the other in `build_win_release`, containing all the appropriate config flags for your system.

## How to use Yolo as DLL and SO libraries

* on Linux - set `LIBSO=1` in the `Makefile` and do `make`
* on Windows - compile `build\darknet\yolo_cpp_dll.sln` or `build\darknet\yolo_cpp_dll_no_gpu.sln` solution

There are 2 APIs:
* C API: https://github.com/AlexeyAB/darknet/blob/master/include/darknet.h
    * Python examples using the C API::     
         * https://github.com/AlexeyAB/darknet/blob/master/darknet.py	
         * https://github.com/AlexeyAB/darknet/blob/master/darknet_video.py
    
* C++ API: https://github.com/AlexeyAB/darknet/blob/master/include/yolo_v2_class.hpp
    * C++ example that uses C++ API: https://github.com/AlexeyAB/darknet/blob/master/src/yolo_console_dll.cpp
    
----

1. To compile Yolo as C++ DLL-file `yolo_cpp_dll.dll` - open the solution `build\darknet\yolo_cpp_dll.sln`, set **x64** and **Release**, and do the: Build -> Build yolo_cpp_dll
    * You should have installed **CUDA 10.0**
    * To use cuDNN do: (right click on project) -> properties -> C/C++ -> Preprocessor -> Preprocessor Definitions, and add at the beginning of line: `CUDNN;`

2. To use Yolo as DLL-file in your C++ console application - open the solution `build\darknet\yolo_console_dll.sln`, set **x64** and **Release**, and do the: Build -> Build yolo_console_dll

    * you can run your console application from Windows Explorer `build\darknet\x64\yolo_console_dll.exe`
    **use this command**: `yolo_console_dll.exe data/coco.names yolov3.cfg yolov3.weights test.mp4`
    
    * after launching your console application and entering the image file name - you will see info for each object: 
    `<obj_id> <left_x> <top_y> <width> <height> <probability>`
    * to use simple OpenCV-GUI you should uncomment line `//#define OPENCV` in `yolo_console_dll.cpp`-file: [link](https://github.com/AlexeyAB/darknet/blob/a6cbaeecde40f91ddc3ea09aa26a03ab5bbf8ba8/src/yolo_console_dll.cpp#L5)
    * you can see source code of simple example for detection on the video file: [link](https://github.com/AlexeyAB/darknet/blob/ab1c5f9e57b4175f29a6ef39e7e68987d3e98704/src/yolo_console_dll.cpp#L75)
   
`yolo_cpp_dll.dll`-API: [link](https://github.com/AlexeyAB/darknet/blob/master/src/yolo_v2_class.hpp#L42)
```
struct bbox_t {
    unsigned int x, y, w, h;    // (x,y) - top-left corner, (w, h) - width & height of bounded box
    float prob;                    // confidence - probability that the object was found correctly
    unsigned int obj_id;        // class of object - from range [0, classes-1]
    unsigned int track_id;        // tracking id for video (0 - untracked, 1 - inf - tracked object)
    unsigned int frames_counter;// counter of frames on which the object was detected
};

class Detector {
public:
        Detector(std::string cfg_filename, std::string weight_filename, int gpu_id = 0);
        ~Detector();

        std::vector<bbox_t> detect(std::string image_filename, float thresh = 0.2, bool use_mean = false);
        std::vector<bbox_t> detect(image_t img, float thresh = 0.2, bool use_mean = false);
        static image_t load_image(std::string image_filename);
        static void free_image(image_t m);

#ifdef OPENCV
        std::vector<bbox_t> detect(cv::Mat mat, float thresh = 0.2, bool use_mean = false);
	std::shared_ptr<image_t> mat_to_image_resize(cv::Mat mat) const;
#endif
};
```

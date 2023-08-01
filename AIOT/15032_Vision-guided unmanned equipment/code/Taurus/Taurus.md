# Taurus部分

## 代码结构

### 路径：

#### 核心逻辑函数文件

\home\openharmony\device\soc\hisilicon\hi3516dv300\sdk_linux\sample\taurus\ai_sample\scenario\cnn_eyelight_classify

#### 可执行文件包含文件

home\openharmony\device\soc\hisilicon\hi3516dv300\sdk_linux\sample\taurus\ai_sample\smp

入口函数位于：sample_ai_main.cpp


## 项目构建过程

参考文件：《Taurus & Pegasus AI计算机视觉基础开发套件学习资料》

1. Taurus镜像烧录，跟随学习资料指引把openharmony烧入Taurus。
2. 跟随学习资料指引搭建出准备好的linux虚拟机系统，并运行学习资料准备好的docker环境，并与电脑搭建nfs文件传输。
3. 在电脑上用vscode打开搭建起的链路文件夹nfs:/home/openharmony/。
4. 参照分类AIoT的demo——trash_clssify搭建自己的项目文件夹，其中至少应该包含一个c文件和一个h头文件，主要修改trash_clssify项目中的CnnTrashClassifyLoadModel、CnnTrashClassifyUnloadModel、CnnTrashClassifyCal、CnnTrashClassifyFlag四个函数，根据自身需求修改逻辑。
5. 修改可执行文件入口sample_ai_main.cpp中处理参数的逻辑，用以调用自己新建的项目函数入口。
6. 在sample_media_ai.c中添加CnnEyeLightClassifyAiProcess、GetVpssChnFrameCnnEyeLightClassify、CnnEyeLightAiThreadProcess、SAMPLE_MEDIA_EYELIGHT_CLASSIFY，参考垃圾分类的函数内容，只需要修改函数之间的调用关系即可。
7. 在虚拟机的终端下cd到/home/openharmony/sdk_linux/sample/build，并执行：make ai_sample_clean && make ai_sample
7. 建立起Taurus和电脑的nfs文件通道，把电脑的文件夹地址挂载到Taurus的/mnt目录。
8. 把\home\openharmony\sdk_linux\sample\output下生成的可执行文件通过nfs传输到Taurus中，并从mnt文件夹复制到userdata文件夹中，并修改权限为777。
9. 跟随学习资料指引通过Taurus进行录像并制作数据集，训练出深度学习模型，并将其量化为wk后缀并复制到userdata中的models文件夹下。
10. 将Taurus连接到目标WIFI。 
11. 运行项目。

## 代码功能（按函数调用顺序说明）

### 调用顺序

main --> SAMPLE_MEDIA_EYELIGHT_CLASSIFY --> CnnEyeLightAiThreadProcess --> CnnEyeLightAiThreadProcess --> GetVpssChnFrameCnnEyeLightClassify --> CnnEyeLightClassifyAiProcess --> CnnEyeLightClassifyLoadModel --> CnnEyeLightClassifyCal --> CnnEyeLightClassifyFlag

### SAMPLE_MEDIA_EYELIGHT_CLASSIFY

将sensor采集到数据显示到液晶屏上，同时创建线程运行垃圾分类推理计算。

视频输入（VI）->视频处理子系统（VPSS）->视频输出（VO）->显示屏（mipi）

```c
HI_S32 SAMPLE_MEDIA_EYELIGHT_CLASSIFY(HI_VOID)
{
    HI_S32             s32Ret;
    HI_S32             fd = 0;

    ViPramCfg(); // 配置VI参数

    s32Ret = SAMPLE_COMM_VI_GetSizeBySensor(g_aicMediaInfo.viCfg.astViInfo[0].stSnsInfo.enSnsType,
        &g_aicMediaInfo.enPicSize); // 通过Sensor型号获取enPicSize
    SAMPLE_CHECK_EXPR_RET(s32Ret != HI_SUCCESS, s32Ret, "get pic size by sensor fail, s32Ret=%#x\n", s32Ret);

    s32Ret = SAMPLE_COMM_SYS_GetPicSize(g_aicMediaInfo.enPicSize, &g_aicMediaInfo.stSize); // 根据enPicSize，得到图片的宽高
    SAMPLE_PRT("AIC: snsMaxSize=%ux%u\n", g_aicMediaInfo.stSize.u32Width, g_aicMediaInfo.stSize.u32Height);
    SAMPLE_CHECK_EXPR_RET(s32Ret != HI_SUCCESS, s32Ret, "get picture size failed, s32Ret=%#x\n", s32Ret);

    StVbParamCfg(&g_aicMediaInfo.vbCfg); // 配置视频缓存池VB参数

    s32Ret = SAMPLE_COMM_SYS_Init(&g_aicMediaInfo.vbCfg); // 视频缓存池初始化以及MPI系统初始化
    SAMPLE_CHECK_EXPR_RET(s32Ret != HI_SUCCESS, s32Ret, "system init failed, s32Ret=%#x\n", s32Ret);

    s32Ret = SAMPLE_VO_CONFIG_MIPI(&fd); //设置VO至MIPI通路，获取MIPI设备
    SAMPLE_CHECK_EXPR_GOTO(s32Ret != HI_SUCCESS, EXIT, "CONFIG MIPI FAIL.s32Ret:0x%x\n", s32Ret);

    VpssParamCfg(); // 配置VPSS参数
    s32Ret = ViVpssCreate(&g_aicMediaInfo.viSess, &g_aicMediaInfo.viCfg, &g_aicMediaInfo.vpssCfg);
    SAMPLE_CHECK_EXPR_GOTO(s32Ret != HI_SUCCESS, EXIT1, "ViVpss Sess create FAIL, ret=%#x\n", s32Ret);
    g_aicMediaInfo.vpssGrp = AIC_VPSS_GRP;
    g_aicMediaInfo.vpssChn0 = AIC_VPSS_ZOUT_CHN;

    StVoParamCfg(&g_aicMediaInfo.voCfg); // 配置VO参数

    s32Ret = SampleCommVoStartMipi(&g_aicMediaInfo.voCfg); // 启动VO到MIPI lcd通路
    SAMPLE_CHECK_EXPR_GOTO(s32Ret != HI_SUCCESS, EXIT1, "start vo FAIL. s32Ret: 0x%x\n", s32Ret);

    s32Ret = SAMPLE_COMM_VPSS_Bind_VO(g_aicMediaInfo.vpssGrp, g_aicMediaInfo.vpssChn0, g_aicMediaInfo.voCfg.VoDev, 0); // VPSS绑定VO
    SAMPLE_CHECK_EXPR_GOTO(s32Ret != HI_SUCCESS, EXIT2, "vo bind vpss FAIL. s32Ret: 0x%x\n", s32Ret);
    SAMPLE_PRT("vpssGrp:%d, vpssChn:%d\n", g_aicMediaInfo.vpssGrp, g_aicMediaInfo.vpssChn0);

    //edit by rh 创建工作线程运行ai
    s32Ret = CnnEyeLightAiThreadProcess();

    SAMPLE_CHECK_EXPR_RET(s32Ret != HI_SUCCESS, s32Ret, "ai proccess thread creat fail:%s\n", strerror(s32Ret));
    Pause();
    g_bAiProcessStopSignal = HI_TRUE;

    pthread_join(g_aiProcessThread, NULL); // 等待一个线程结束，线程间同步的操作
    g_aiProcessThread = 0;
    PauseDoUnloadCnnModel();

    SAMPLE_COMM_VPSS_UnBind_VO(g_aicMediaInfo.vpssGrp, g_aicMediaInfo.vpssChn0, g_aicMediaInfo.voCfg.VoDev, 0);
    SAMPLE_VO_DISABLE_MIPITx(fd);
    SampleCloseMipiTxFd(fd);
    system("echo 0 > /sys/class/gpio/gpio55/value");

EXIT2:
    SAMPLE_COMM_VO_StopVO(&g_aicMediaInfo.voCfg);
EXIT1:
    VpssStop(&g_aicMediaInfo.vpssCfg);
    SAMPLE_COMM_VI_UnBind_VPSS(g_aicMediaInfo.viCfg.astViInfo[0].stPipeInfo.aPipe[0],
        g_aicMediaInfo.viCfg.astViInfo[0].stChnInfo.ViChn, g_aicMediaInfo.vpssGrp);
    ViStop(&g_aicMediaInfo.viCfg);
    free(g_aicMediaInfo.viSess);
EXIT:
    SAMPLE_COMM_SYS_Exit();
    return s32Ret;
}
```

### CnnEyeLightAiThreadProcess

创建帧提取与AI处理线程

```c
static HI_S32 CnnEyeLightAiThreadProcess(HI_VOID)
{
    HI_S32 s32Ret;
    if (snprintf_s(acThreadName, BUFFER_SIZE, BUFFER_SIZE - 1, "AIProcess") < 0) {
        HI_ASSERT(0);
    }
    prctl(PR_SET_NAME, (unsigned long)acThreadName, 0, 0, 0);
    s32Ret = pthread_create(&g_aiProcessThread, NULL, GetVpssChnFrameCnnEyeLightClassify, NULL);

    return s32Ret;
}
```

### GetVpssChnFrameCnnEyeLightClassify

从vpss获取视频帧图像，传入ai处理逻辑中。

```c
static HI_VOID* GetVpssChnFrameCnnEyeLightClassify(HI_VOID* arg)
{
    int ret;
    VIDEO_FRAME_INFO_S frm;
    HI_S32 s32MilliSec = 20000;

    while (HI_FALSE == g_bAiProcessStopSignal) {
        ret = HI_MPI_VPSS_GetChnFrame(g_aicMediaInfo.vpssGrp, g_aicMediaInfo.vpssChn0, &frm, s32MilliSec);
        if (ret != 0) {
            SAMPLE_PRT("HI_MPI_VPSS_GetChnFrame FAIL, err=%#x, grp=%d, chn=%d\n",
                ret, g_aicMediaInfo.vpssGrp, g_aicMediaInfo.vpssChn0);
            ret = HI_MPI_VPSS_ReleaseChnFrame(g_aicMediaInfo.vpssGrp, g_aicMediaInfo.vpssChn0, &frm);
            if (ret != HI_SUCCESS) {
                SAMPLE_PRT("Error(%#x),HI_MPI_VPSS_ReleaseChnFrame failed,Grp(%d) chn(%d)!\n",
                    ret, g_aicMediaInfo.vpssGrp, g_aicMediaInfo.vpssChn0);
            }
            continue;
        }
        if (g_num == 0) {
            ConfBaseInit(AI_SAMPLE_CFG_FILE);
            g_num++;
        }
        CnnEyeLightClassifyAiProcess(frm);
    }

    return HI_NULL;
}
```

### CnnEyeLightClassifyAiProcess

加载神经网络模型，调用ai处理帧的函数。

```c
static HI_VOID CnnEyeLightClassifyAiProcess(VIDEO_FRAME_INFO_S frm)
{
    int ret;
    if (GetCfgBool("eyelight_classify_switch:support_eyelight_classify", true)) { //判断由用户控制的config文件中设定的运行函数是否包含此函数
        if (g_workPlug.model == 0) {
            HI_ASSERT(!g_aicMediaInfo.osds);
            g_aicMediaInfo.osds = OsdsCreate(HI_OSD_BINDMOD_VPSS, g_aicMediaInfo.vpssGrp, g_aicMediaInfo.vpssChn0);  // 用于创建叠加在数据流上的osd图层，但在本项目中没有作用
            HI_ASSERT(g_aicMediaInfo.osds);
            //edit by rh  加载模型并绑定到信息结构体中
            ret = CnnEyeLightClassifyLoadModel(&g_workPlug.model, g_aicMediaInfo.osds);

            if (ret < 0) {
                g_workPlug.model = 0;
                SAMPLE_CHECK_EXPR_GOTO(ret < 0, TRASH_RELEASE,
                    "load cnn EyeLight classify model err(%#x)\n", ret);
            }
        }
        VIDEO_FRAME_INFO_S *resFrm = NULL;
        //edit by rh
        ret = CnnEyeLightClassifyCal(g_workPlug.model, &frm, resFrm);  // 使用模型对帧进行分类
        SAMPLE_CHECK_EXPR_GOTO(ret < 0, TRASH_RELEASE,
            "EyeLight classify plug cal FAIL, ret=%#x\n", ret);
    }

    TRASH_RELEASE:
        ret = HI_MPI_VPSS_ReleaseChnFrame(g_aicMediaInfo.vpssGrp, g_aicMediaInfo.vpssChn0, &frm);
        if (ret != HI_SUCCESS) {
            SAMPLE_PRT("Error(%#x),HI_MPI_VPSS_ReleaseChnFrame failed,Grp(%d) chn(%d)!\n",
                ret, g_aicMediaInfo.vpssGrp, g_aicMediaInfo.vpssChn0);
        }
}
```

### CnnEyeLightClassifyLoadModel

加载训练好的模型。

```c
HI_S32 CnnEyeLightClassifyLoadModel(uintptr_t* model, OsdSet* osds)
{
    SAMPLE_SVP_NNIE_CFG_S *self = NULL;
    HI_S32 ret;

    // osd部分都没有使用
    /*HI_CHAR audioThreadName[BUFFER_SIZE] = {0};

    ret = OsdLibInit();
    HI_ASSERT(ret == HI_SUCCESS);

    g_osdsTrash = osds;
    HI_ASSERT(g_osdsTrash);
    g_osd0Trash = OsdsCreateRgn(g_osdsTrash);
    HI_ASSERT(g_osd0Trash >= 0);*/

    ret = CnnCreate(&self, MODEL_FILE_EYELIGHT); // 将训练好的模型地址MODEL_FILE_EYELIGHT引入

    *model = ret < 0 ? 0 : (uintptr_t)self;
    SAMPLE_PRT("load cnn eye light classify model, ret:%d\n", ret);

    return ret;
}
```

### CnnEyeLightClassifyCal

先进行预处理，再使用NNIE进行硬件加速推理，并调用推理结果加工函数，将加工信息通过网络链路发送到目标ip

```c
HI_S32 CnnEyeLightClassifyCal(uintptr_t model, VIDEO_FRAME_INFO_S *srcFrm, VIDEO_FRAME_INFO_S *resFrm)
{
    SAMPLE_SVP_NNIE_CFG_S *self = (SAMPLE_SVP_NNIE_CFG_S*)model; 
    IVE_IMAGE_S img; 
    RectBox cnnBoxs[DETECT_OBJ_MAX] = {0};
    VIDEO_FRAME_INFO_S resizeFrm;  
    static HI_CHAR prevOsd[NORM_BUF_SIZE] = "";
    HI_CHAR osdBuf[NORM_BUF_SIZE] = "";
    
    RecogNumInfo resBuf[RET_NUM_MAX] = {0};
    HI_S32 resLen = 0;
    HI_S32 ret;
    IVE_IMAGE_S imgIn;

    cnnBoxs[0].xmin = MIN_OF_BOX;
    cnnBoxs[0].xmax = MAX_OF_BOX;
    cnnBoxs[0].ymin = MIN_OF_BOX;
    cnnBoxs[0].ymax = MAX_OF_BOX;

    ret = MppFrmResize(srcFrm, &resizeFrm, FRM_WIDTH, FRM_HEIGHT);  // resize 256*256
    SAMPLE_CHECK_EXPR_RET(ret != HI_SUCCESS, ret, "for resize FAIL, ret=%x\n", ret);

    ret = FrmToOrigImg(&resizeFrm, &img);
    SAMPLE_CHECK_EXPR_RET(ret != HI_SUCCESS, ret, "for Frm2Img FAIL, ret=%x\n", ret);

    ret = ImgYuvCrop(&img, &imgIn, &cnnBoxs[0]); // Crop the image to classfication network
    SAMPLE_CHECK_EXPR_RET(ret < 0, ret, "ImgYuvCrop FAIL, ret=%x\n", ret);

    ret = CnnCalImg(self, &imgIn, resBuf, sizeof(resBuf) / sizeof((resBuf)[0]), &resLen);
    SAMPLE_CHECK_EXPR_RET(ret < 0, ret, "cnn cal FAIL, ret=%x\n", ret);

    HI_ASSERT(resLen <= sizeof(resBuf) / sizeof(resBuf[0]));

    ret = CnnEyeLightClassifyFlag(resBuf, resLen, osdBuf, sizeof(osdBuf)); // 根据模型返回的分类结果进行逻辑处理
    SAMPLE_CHECK_EXPR_RET(ret < 0, ret, "CnnEyeLightClassifyFlag cal FAIL, ret=%x\n", ret);

    struct sockaddr_in sin = {0};
    struct sockaddr_in serverAddr = {0};

    /* create socket */
    int sClient = socket(AF_INET, SOCK_DGRAM, 0);
    if (sClient < 0) {
        SAMPLE_PRT("create socket Fialed\r\n");
        close(sClient);
        IveImgDestroy(&imgIn);
        MppFrmDestroy(&resizeFrm);
        return -1;
    }

    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);

    if (inet_pton(AF_INET, SERVER_IP, &serverAddr.sin_addr) <= 0) { // 将点分文本格式的目标ip地址转换为二进制网络字节序
        SAMPLE_PRT("inet_pton fail!");
        close(sClient);
        IveImgDestroy(&imgIn);
        MppFrmDestroy(&resizeFrm);
        return -1;
    }

    if (strcmp(osdBuf, prevOsd) != 0) {  //仅当计算结果与之前计算发生变化时，才发送数据
        HiStrxfrm(prevOsd, osdBuf, sizeof(prevOsd));

        if(sendto(sClient, osdBuf, strlen(osdBuf), 0, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0){
            SAMPLE_PRT("sendto fail!");
        }else{
            SAMPLE_PRT("sendto successed!!!!!!!!!!!!!!");
        }
    }
    

    IveImgDestroy(&imgIn);
    MppFrmDestroy(&resizeFrm);
    close(sClient);

    //return ret;
    return 0;
}

```

### CnnEyeLightClassifyFlag

根据推理结果进行业务处理

```c
static HI_S32 CnnEyeLightClassifyFlag(const RecogNumInfo items[], HI_S32 itemNum, HI_CHAR* buf, HI_S32 size)
{
    HI_CHAR *eyeLightPosition = NULL;

    for (HI_U32 i = 0; i < itemNum; i++) {
        const RecogNumInfo *item = &items[i];
        uint32_t score = item->score * HI_PER_BASE / SCORE_MAX;
        if (score < THRESH_MIN) {
            break;
        }
        SAMPLE_PRT("----eye light position flag----num:%d, score:%d\n", item->num, score);
        switch (item->num) { // a左，w中，d右
            case 0u:
                eyeLightPosition = "a";
                break;
            case 1u:
                eyeLightPosition = "w";
                break;
            case 2u:
                eyeLightPosition = "d";
                break;
            default:
                break;
        }
    }
    snprintf_s(buf, size, size - 1, "%s", eyeLightPosition); // 将信息绑定到buf以回传

    return HI_SUCCESS;
}
```





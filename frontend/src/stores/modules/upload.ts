import { ref } from 'vue';
import { ElMessage } from 'element-plus';

export function useUpload(options: {
    uploadApi: (data: any, onProgress?: (percent: number) => void) => Promise<any>,
    formDataBuilder?: (rawFile: any) => any
}) {
    const fileList = ref<any[]>([]);
    const uploading = ref(false);
    const is_uploaded = ref(false); // 是否上传完成
    const progressList = ref<number[]>([]); // 每个文件的进度

    function onFileChange(uploadFile: any, uploadFiles: any[]) {
        fileList.value = uploadFiles;
        progressList.value = uploadFiles.map(() => 0);
        console.log('Selected files:', uploadFiles);
    }

    function onFileRemove(file: any, uploadFiles: any[]) {
        fileList.value = uploadFiles;
        progressList.value = uploadFiles.map(() => 0);
    }

    const uploadFile = async () => {
        if (!fileList.value.length) {
            ElMessage.error('请选择文件');
            return;
        }
        uploading.value = true;
        is_uploaded.value = false; // 初始为false
        let allSuccess = true; // 标记所有文件是否都成功

        for (let i = 0; i < fileList.value.length; i++) {
            const rawFile = fileList.value[i].raw ?? fileList.value[i];
            const data = options.formDataBuilder
                ? options.formDataBuilder(rawFile)
                : (() => {
                    const fd = new FormData();
                    fd.append('file', rawFile, rawFile.name);
                    return fd;
                })();

            // 进度回调
            const onProgress = (percent: number) => {
                progressList.value[i] = percent;
                fileList.value[i].percentage = percent;
            };

            try {
                const response = await options.uploadApi(data, onProgress);
                if (response.code === 0) {
                    fileList.value[i].status = 'success';
                    progressList.value[i] = 100;
                    ElMessage.success('文件上传完成');
                } else {
                    fileList.value[i].status = 'error';
                    allSuccess = false;
                    ElMessage.error(response.data?.message || '上传失败');
                }
            } catch (error) {
                fileList.value[i].status = 'error';
                allSuccess = false;
                ElMessage.error('上传失败');
            }
        }

        is_uploaded.value = allSuccess; // 只有全部成功才为true
        uploading.value = false;
    };



    return {
        fileList,
        uploading,
        is_uploaded,
        progressList,
        onFileChange,
        onFileRemove,
        uploadFile,
    };
}
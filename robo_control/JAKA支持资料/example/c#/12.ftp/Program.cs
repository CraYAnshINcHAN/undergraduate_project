using jakaApi;
using jkType;
using System;
using System.Text;

class Program
{
    static void SetEnvironment()
    {
        string cur_path = Environment.CurrentDirectory;
        string[] paths = cur_path.Split("example");
        var path = Environment.GetEnvironmentVariable("PATH");
        //此处指定jakaApi.dll和jakaApi.lib的路径
        Environment.SetEnvironmentVariable("PATH", Path.Join(paths[0], "out\\shared\\Release\\") + ";" + path);
    }

    static void assert_0_or_exit(int ret, string msg)
    {
        if (ret != 0)
        {
            Console.WriteLine("{0}({1}) failed.", msg, ret);
            System.Environment.Exit(-1);
        }
    }

    public static void Main(string[] args)
    {
        SetEnvironment();

        int handle = 0;
        int result = jakaAPI.create_handler("192.168.137.173".ToCharArray(), ref handle);

        string local = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\testfile";
        string local_download = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\testfile.tmp";
        string remote = @"log/testfile";
        string remote_new = @"log/testfile.tmp";

        // 文件操作
        int errno = jakaAPI.upload_file(ref handle, local.ToCharArray(), remote.ToCharArray(), 1);
        assert_0_or_exit(errno, "upload file");

        errno = jakaAPI.rename_ftp_file(ref handle, remote.ToCharArray(), remote_new.ToCharArray(), 1);
        assert_0_or_exit(errno, "rename file");

        errno = jakaAPI.download_file(ref handle, local_download.ToCharArray(), remote_new.ToCharArray(), 1);
        assert_0_or_exit(errno, "download file");

        errno = jakaAPI.del_ftp_file(ref handle, remote_new.ToCharArray(), 1);
        assert_0_or_exit(errno, "del file");

        local = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\test_dir";
        local_download = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\test_dir.tmp";
        remote = @"log/test_dir";
        remote_new = @"log/test_dir.tmp";

        // 目录操作
        errno = jakaAPI.upload_file(ref handle, local.ToCharArray(), remote.ToCharArray(), 2);
        assert_0_or_exit(errno, "upload dir");

        errno = jakaAPI.rename_ftp_file(ref handle, remote.ToCharArray(), remote_new.ToCharArray(), 2);
        assert_0_or_exit(errno, "rename dir");

        errno = jakaAPI.download_file(ref handle, local_download.ToCharArray(), remote_new.ToCharArray(), 2);
        assert_0_or_exit(errno, "download dir");

        errno = jakaAPI.del_ftp_file(ref handle, remote_new.ToCharArray(), 2);
        assert_0_or_exit(errno, "del dir");

        local = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\测试文件";
        local_download = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\测试文件.tmp";
        remote = @"log/测试文件";
        remote_new = @"log/测试文件.tmp";

        // 文件操作
        errno = jakaAPI.upload_file(ref handle, local.ToCharArray(), remote.ToCharArray(), 1);
        assert_0_or_exit(errno, "upload cn file");

        errno = jakaAPI.rename_ftp_file(ref handle, remote.ToCharArray(), remote_new.ToCharArray(), 1);
        assert_0_or_exit(errno, "rename cn file");

        errno = jakaAPI.download_file(ref handle, local_download.ToCharArray(), remote_new.ToCharArray(), 1);
        assert_0_or_exit(errno, "download cn file");

        errno = jakaAPI.del_ftp_file(ref handle, remote_new.ToCharArray(), 1);
        assert_0_or_exit(errno, "del cn file");

        local = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\测试目录";
        local_download = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\测试目录.tmp";
        remote = @"log/测试目录";
        remote_new = @"log/测试目录.tmp";

        // 目录操作
        errno = jakaAPI.upload_file(ref handle, local.ToCharArray(), remote.ToCharArray(), 2);
        assert_0_or_exit(errno, "upload cn dir");

        errno = jakaAPI.rename_ftp_file(ref handle, remote.ToCharArray(), remote_new.ToCharArray(), 2);
        assert_0_or_exit(errno, "rename cn dir");

        errno = jakaAPI.download_file(ref handle, local_download.ToCharArray(), remote_new.ToCharArray(), 2);
        assert_0_or_exit(errno, "download cn dir");

        errno = jakaAPI.del_ftp_file(ref handle, remote_new.ToCharArray(), 2);
        assert_0_or_exit(errno, "del cn dir");

        local = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\测试 文件";
        local_download = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\测试 文件.tmp";
        remote = @"log/测试 文件";
        remote_new = @"log/测试 文件.tmp";

        // 文件操作
        errno = jakaAPI.upload_file(ref handle, local.ToCharArray(), remote.ToCharArray(), 1);
        assert_0_or_exit(errno, "upload cn sp file");

        errno = jakaAPI.rename_ftp_file(ref handle, remote.ToCharArray(), remote_new.ToCharArray(), 1);
        assert_0_or_exit(errno, "rename cn sp file");

        errno = jakaAPI.download_file(ref handle, local_download.ToCharArray(), remote_new.ToCharArray(), 1);
        assert_0_or_exit(errno, "download cn sp file");

        errno = jakaAPI.del_ftp_file(ref handle, remote_new.ToCharArray(), 1);
        assert_0_or_exit(errno, "del cn sp file");

        local = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\测试 目录";
        local_download = @"C:\Users\jenkins\Desktop\sdk_dev\jakaAPI-c\jakaAPI-c\测试 目录.tmp";
        remote = @"log/测试 目录";
        remote_new = @"log/测试 目录.tmp";

        // 目录操作
        errno = jakaAPI.upload_file(ref handle, local.ToCharArray(), remote.ToCharArray(), 2);
        assert_0_or_exit(errno, "upload cn sp dir");

        errno = jakaAPI.rename_ftp_file(ref handle, remote.ToCharArray(), remote_new.ToCharArray(), 2);
        assert_0_or_exit(errno, "rename cn sp dir");

        errno = jakaAPI.download_file(ref handle, local_download.ToCharArray(), remote_new.ToCharArray(), 2);
        assert_0_or_exit(errno, "download cn sp dir");

        // 查看文件列表
        string remote_get_dir = "log";
        StringBuilder remote_get_res = new StringBuilder(4096);
        errno = jakaAPI.get_ftp_dir(ref handle, remote_get_dir, 0, remote_get_res);
        assert_0_or_exit(errno, "get ftp dir");
        Console.WriteLine("get_ftp_dir res: {0}", remote_get_res);

        errno = jakaAPI.del_ftp_file(ref handle, remote_new.ToCharArray(), 2);
        assert_0_or_exit(errno, "del cn sp dir");

        jakaAPI.destory_handler(ref handle);
    }
}

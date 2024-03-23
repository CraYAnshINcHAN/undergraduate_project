using jakaApi;
using jkType;

class Program
{
    static void SetEnvironment()
    {
        string cur_path = Environment.CurrentDirectory;
        string[] paths = cur_path.Split("example");
        var path = Environment.GetEnvironmentVariable("PATH");
        Environment.SetEnvironmentVariable("PATH", Path.Join(paths[0], "out\\shared\\Release\\") + ";" + path);
    }

    public static void Main(string[] args)
    {
        SetEnvironment();

        int handle = 0;
        double thresholding;
        int result = jakaAPI.create_handler("192.168.137.173".ToCharArray(), ref handle);
        jakaAPI.power_on(ref handle);//机器人上电
        jakaAPI.enable_robot(ref handle);//机器人上使能

        jakaAPI.get_in_pos_thresholding(ref handle, out thresholding);
        Console.WriteLine("thresholding {0}", thresholding);

        jakaAPI.disable_robot(ref handle);
        jakaAPI.power_off(ref handle);
    }
}

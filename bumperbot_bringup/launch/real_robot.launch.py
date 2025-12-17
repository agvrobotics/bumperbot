import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    use_slam = LaunchConfiguration("use_slam")

    use_slam_arg = DeclareLaunchArgument(
        "use_slam",
        default_value="false"
    )
    use_master_arg = DeclareLaunchArgument(
        "use_master",
        default_value="False",
    )
    use_master = LaunchConfiguration("use_master")

    master = GroupAction(
        condition = IfCondition(use_master),
        actions = [
            Node(
                package="joy",
                executable="joy_node",
                name="joystick",
                parameters=[os.path.join(get_package_share_directory("bumperbot_controller"), "config", "joy_config.yaml"),
                            {"use_sim_time": False}],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                arguments=["-d", os.path.join(
                        get_package_share_directory("nav2_bringup"),
                        "rviz",
                        "nav2_default_view.rviz"
                    )
                ],
                output="screen",
                parameters=[{"use_sim_time": False}],
            ),
        ]
    )

    slave = GroupAction(
        condition = UnlessCondition(use_master),
        actions = [
            Node(
                package="rplidar_ros",
                executable="rplidar_node",
                name="rplidar_node",
                parameters=[os.path.join(
                    get_package_share_directory("bumperbot_bringup"),
                    "config",
                    "rplidar_a1.yaml"
                )],
                output="screen"
            ),
            TimerAction(
                period=3.0,
                actions=[
                    IncludeLaunchDescription(
                        os.path.join(
                            get_package_share_directory("bumperbot_firmware"),
                            "launch",
                            "hardware_interface.launch.py"
                        ),
                    ),

                    
                    IncludeLaunchDescription(
                        os.path.join(
                            get_package_share_directory("bumperbot_controller"),
                            "launch",
                            "controller.launch.py"
                        ),
                        launch_arguments={
                            "use_simple_controller": "False",
                            "use_python": "False"
                        }.items(),
                    ),


                    IncludeLaunchDescription(
                        os.path.join(
                            get_package_share_directory("bumperbot_localization"),
                            "launch",
                            "global_localization.launch.py"
                        ),
                        condition=UnlessCondition(use_slam)
                    ),

                    IncludeLaunchDescription(
                        os.path.join(
                            get_package_share_directory("bumperbot_mapping"),
                            "launch",
                            "slam.launch.py"
                        ),
                        condition=IfCondition(use_slam)
                    ),
                    IncludeLaunchDescription(
                        os.path.join(
                            get_package_share_directory("bumperbot_controller"),
                            "launch",
                            "joystick_teleop.launch.py"
                        ),
                        launch_arguments={
                            "use_sim_time": "False"
                        }.items()
                    ),
                    IncludeLaunchDescription(
                        os.path.join(
                            get_package_share_directory("bumperbot_navigation"),
                            "launch",
                            "navigation.launch.py"
                        ),
                    ),
                    Node(
                        package="bumperbot_utils",
                        executable="safety_stop.py",
                        output="screen"
                    ),
                ]
            )
        ]
    )
    
    return LaunchDescription([
        use_slam_arg,
        use_master_arg,
        master,
        slave,
    ])
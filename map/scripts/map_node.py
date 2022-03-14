#!/usr/bin/env python

import rospy
import yaml
import tf

# from std_msgs.msg import String
from map.msg import StringArray
from map.srv import SaveLocal, SaveLocalResponse

ROS_RATE = 10
PUBLISHER_QUEUE_SIZE = 10

class Map:
    """docstring for map"""
    def __init__(self):

        self.rate = rospy.Rate(ROS_RATE)
        self.tb = tf.TransformBroadcaster()
        self.pub = rospy.Publisher('locals', StringArray, queue_size=PUBLISHER_QUEUE_SIZE)
        rospy.Service('/map/save_local', SaveLocal, self.handle_start)

        fname = rospy.get_param("locals_file")
        yaml_file = open(fname,'r')
        yaml_data = yaml.load(yaml_file)
        self.locals = yaml_data['locals']

        while not rospy.is_shutdown():
            self.tb.sendTransform(
                (0,0,0),
                (0,0,0,1),
                rospy.Time.now(),
                "locals",
                "map")

            sa = StringArray()
            for target in yaml_data['locals']:
                sa.strings.append(target)
                x = self.locals[target][0][0]
                y = self.locals[target][0][1]
                z = self.locals[target][1][2]
                w = self.locals[target][1][3]

                self.tb.sendTransform(
                    (x, y, 0),
                    (0,0,z,w),
                    rospy.Time.now(),
                    target,
                    "locals")

            self.pub.publish(sa)
            self.rate.sleep()


    def handle_start(self, req):

        fname = rospy.get_param("/locals_file")
        yaml_file = open(fname,'r')
        yaml_data = yaml.load(yaml_file)
        keys = yaml_data['locals'].keys()

        yaml_data['locals'][req.name] = [[req.pose.position.x,req.pose.position.y],[req.pose.orientation.x,req.pose.orientation.y,req.pose.orientation.z,req.pose.orientation.w]]

        yaml_file = open(fname,'w')
        yaml_file.write( yaml.dump(yaml_data, default_flow_style=False))

        self.locals = yaml_data['locals']

        info = req.name + " saved!"
        rospy.loginfo(info)
        return SaveLocalResponse(True, info)

if __name__ == "__main__":
    rospy.init_node('map')
    Map()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")


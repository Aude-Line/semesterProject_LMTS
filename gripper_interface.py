#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from std_srvs.srv import Trigger
from ros2_fp_core_msgs.srv import MoveTool
from ros2_fp_core_msgs.srv import MoveJoint
from ros2_fp_core_msgs.srv import Initialize
from ros2_fp_core_msgs.srv import Calibrate
from ros2_fp_core_msgs.srv import InverseKinematics

Z_CLEARANCE_MM = 100.0


class GripperInterface(Node):
	def __init__(self) -> None:
		super().__init__('gripper_interface')
		self.pub = self.create_publisher(Int32, 'esp32_rx_int32', 10)
		self.target = None
		self.place = None
		self.move_tool_client = self.create_client(MoveTool, '/PRob2R/core/move_tool')
		self.move_joint_client = self.create_client(MoveJoint, '/PRob2R/core/move_joint')
		self.inverse_kinematics_client = self.create_client(InverseKinematics, '/PRob2R/core/inverse_kinematics')
		self.connect_client = self.create_client(Initialize, '/PRob2R/core/connect')
		self.disconnect_client = self.create_client(Trigger, '/PRob2R/core/disconnect')
		self.calibrate_client = self.create_client(Calibrate, '/PRob2R/core/calibrate')

	def is_reachable(self, position, position_name: str) -> bool:
		if not self.inverse_kinematics_client.wait_for_service(timeout_sec=2.0):
			print('InverseKinematics service unavailable: /PRob2R/core/inverse_kinematics')
			return False

		x, y, z, angle = position
		req = InverseKinematics.Request()
		req.x = float(x)
		req.y = float(y)
		req.z = float(z)
		req.orientation = [180.0, 0.0, float(angle)]
		req.previous_angles = []

		future = self.inverse_kinematics_client.call_async(req)
		rclpy.spin_until_future_complete(self, future)
		resp = future.result()
		if resp is None:
			print(f'IK check failed for {position_name}: no response')
			return False

		if not resp.success:
			print(f'IK check failed for {position_name}: {resp.message}')
			return False

		print(f'IK check OK for {position_name}. Joint angles: {list(resp.joint_angles)}')
		return True

	def publish_esp_value(self, value: int) -> None:
		msg = Int32()
		msg.data = value
		self.pub.publish(msg)
		self.get_logger().info(f'Published {value} on esp32_rx_int32')

	def move_tool(self, x: float, y: float, z: float, relative: bool, orientation=None) -> bool:
		if not self.move_tool_client.wait_for_service(timeout_sec=2.0):
			print('MoveTool service is not available: /PRob2R/core/move_tool')
			return False

		req = MoveTool.Request()
		req.x = float(x)
		req.y = float(y)
		req.z = float(z)
		req.orientation = [] if orientation is None else [int(v) for v in orientation]
		req.velocity = 20.0
		req.acceleration = 30.0
		req.block = True
		req.relative = relative
		req.frame = 'tool' if relative else 'base'

		future = self.move_tool_client.call_async(req)
		rclpy.spin_until_future_complete(self, future)
		resp = future.result()
		if resp is None:
			print('MoveTool call failed: no response')
			return False

		print(f'MoveTool response: success={resp.success}, message="{resp.message}"')
		return bool(resp.success)

	def connect_robot(self) -> bool:
		if not self.connect_client.wait_for_service(timeout_sec=2.0):
			print('Connect service unavailable: /PRob2R/core/connect')
			return False

		connect_req = Initialize.Request()
		connect_req.robot_kind = 'Connect to Robot'
		connect_req.robot_name = 'PRob2R'
		future = self.connect_client.call_async(connect_req)
		rclpy.spin_until_future_complete(self, future)
		connect_resp = future.result()
		if connect_resp is None or not connect_resp.success:
			msg = '' if connect_resp is None else connect_resp.message
			print(f'Connect failed: {msg}')
			return False
		print(f'Connect: success, message="{connect_resp.message}"')

		if not self.calibrate_client.wait_for_service(timeout_sec=2.0):
			print('Calibrate service unavailable: /PRob2R/core/calibrate')
			return False
		cal_req = Calibrate.Request()
		cal_future = self.calibrate_client.call_async(cal_req)
		rclpy.spin_until_future_complete(self, cal_future)
		cal_resp = cal_future.result()
		if cal_resp is None or not cal_resp.success:
			msg = '' if cal_resp is None else cal_resp.message
			print(f'Calibrate failed: {msg}')
			return False
		print(f'Calibrate: success, message="{cal_resp.message}"')
		return True

	def disconnect_robot(self) -> bool:
		if not self.disconnect_client.wait_for_service(timeout_sec=2.0):
			print('Disconnect service unavailable: /PRob2R/core/disconnect')
			return False

		future = self.disconnect_client.call_async(Trigger.Request())
		rclpy.spin_until_future_complete(self, future)
		resp = future.result()
		if resp is None:
			print('Disconnect failed: no response')
			return False

		print(f'Disconnect: success={resp.success}, message="{resp.message}"')
		return bool(resp.success)

	def demo_move(self) -> None:
		ok = self.move_tool(300.0, -300.0, 400.0, False, [180, 0, 0])
		if not ok:
			print('Demo move failed.')
			return
		print('Demo move finished.')

	def go_home(self) -> None:
		if not self.move_joint_client.wait_for_service(timeout_sec=2.0):
			print('MoveJoint service unavailable: /PRob2R/core/move_joint')
			return

		req = MoveJoint.Request()
		req.actuator_ids = [1, 2, 3, 4, 5, 6]
		req.position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
		req.velocity = 10.0
		req.acceleration = 20.0
		req.block = True
		req.relative = False

		future = self.move_joint_client.call_async(req)
		rclpy.spin_until_future_complete(self, future)
		resp = future.result()
		if resp is None:
			print('Home move failed: no response from MoveJoint.')
			return

		print(f'Home move response: success={resp.success}, message="{resp.message}"')

	def go_to_position(self, position, position_name: str) -> None:
		if position is None:
			print(f'No {position_name} in memory. Set one with: {position_name} x y z angle')
			return

		tx, ty, tz, angle = position

		# Keep the tool head parallel to the table (fixed roll/pitch),
		# allowing only wrist yaw in table plane from target angle.
		table_parallel_orientation = [180, 0, int(angle)]

		# 1) Relative move: go up 10 cm from current position.
		if not self.move_tool(0.0, 0.0, -Z_CLEARANCE_MM, True, [0, 0, 0]):
			print(f'go{position_name.capitalize()} stopped at step 1.')
			return

		# 2) Absolute move: go to 10 cm above target.
		if not self.move_tool(tx, ty, tz + Z_CLEARANCE_MM, False, table_parallel_orientation):
			print(f'go{position_name.capitalize()} stopped at step 2.')
			return

		# 3) Absolute move: go to exact target.
		if not self.move_tool(tx, ty, tz, False, table_parallel_orientation):
			print(f'go{position_name.capitalize()} stopped at step 3.')
			return

		print(f'go{position_name.capitalize()} finished successfully.')

	def go_target(self) -> None:
		self.go_to_position(self.target, 'target')

	def go_place(self) -> None:
		self.go_to_position(self.place, 'place')


def main() -> None:
	rclpy.init()
	node = GripperInterface()

	print('Ready. Available commands:')
	print('  connect             -> connect + calibrate (check response messages)')
	print('  disconnect          -> disconnect robot session')
	print('  demo                -> MoveTool to (400, -400, 400), [180, 0, 0] to fix the gripper on the robot')
	print('  home                -> put the robot in upright home position (all joints to 0)')
	print('  open                -> publish 0 to esp32_rx_int32')
	print('  close               -> publish 1 to esp32_rx_int32')
	print('  target x y z angle  -> store target coordinates + angle in memory')
	print('  place x y z angle   -> store place coordinates + angle in memory')
	print('  gotarget            -> run 3-step MoveTool sequence to target')
	print('  goplace             -> run 3-step MoveTool sequence to place')
	print('  show                -> display stored target/place values')
	print('  q                   -> quit')

	try:
		while rclpy.ok():
			raw = input('> ').strip()
			choice = raw.lower()
			parts = raw.split()

			if choice == 'connect':
				node.connect_robot()

			elif choice == 'disconnect':
				node.disconnect_robot()

			elif choice == 'open':
				node.publish_esp_value(0)

			elif choice == 'close':
				node.publish_esp_value(1)

			elif choice == 'q':
				break

			elif len(parts) == 5 and parts[0].lower() in ('target', 'place'):
				label = parts[0].lower()
				try:
					x = float(parts[1])
					y = float(parts[2])
					z = float(parts[3])
					angle = float(parts[4])
				except ValueError:
					print('Invalid format. Use: target x y z angle or place x y z angle')
					continue

				coords = (x, y, z, angle)
				if not node.is_reachable(coords, label):
					print(f'{label.capitalize()} not saved (point unreachable by IK).')
					continue

				if label == 'target':
					node.target = coords
					print(f'Target saved in memory: {node.target}')
				else:
					node.place = coords
					print(f'Place saved in memory: {node.place}')

			elif choice == 'show':
				print(f'Target: {node.target}')
				print(f'Place: {node.place}')

			elif choice == 'gotarget':
				node.go_target()

			elif choice == 'goplace':
				node.go_place()

			elif choice == 'demo':
				node.demo_move()

			elif choice == 'home':
				node.go_home()

			else:
				print('Unknown command. Use connect, disconnect, home, open, close, target x y z angle, place x y z angle, gotarget, goplace, demo, show, or q.')

	except KeyboardInterrupt:
		pass
	finally:
		node.destroy_node()
		rclpy.shutdown()


if __name__ == '__main__':
	main()

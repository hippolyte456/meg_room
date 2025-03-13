
class EyeTracking:
    pass


# class EyeTracking:
#     def __init__(self, window):
#         self.window = window
#         self.tracker = None
#         self.calibration = None

#     def connect(self):
#         try:
#             self.tracker = tobii_research.find_all_eyetrackers()[0]
#             self.tracker.subscribe_to(tobii_research.EYETRACKER_GAZE_DATA, self.gaze_data_callback, as_dictionary=True)
#         except IndexError:
#             print("No eye tracker found")

#     def gaze_data_callback(self, gaze_data):
#         gaze_data = gaze_data['left_gaze_point_on_display_area']
#         if gaze_data is not None:
#             x, y = self.window.size[0] * gaze_data[0], self.window.size[1] * gaze_data[1]
#             print(x, y)

#     def calibrate(self):
#         self.calibration = tobii_research.ScreenBasedCalibration(self.tracker)
#         self.calibration.enter_calibration_mode()
#         self.calibration.start_calibration()
#         self.calibration.collect_data()
#         self.calibration.leave_calibration_mode()

#     def close(self):
#         self.tracker.unsubscribe_from(tobii_research.EYETRACKER_GAZE_DATA, self.gaze_data_callback)
#         self.tracker = None
#         self.calibration = None
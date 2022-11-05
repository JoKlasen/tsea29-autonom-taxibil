import cv2
import numpy as np
from PIL import Image

TESTFILE = "CI_22.11.05.00.11.17.jpg"



if __name__ == "__main__":
	
	image = Image.open(TESTFILE)
	ori = cv2.imread(TESTFILE)


	cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

	_, threshed = cv2.threshold(cvt_image[:,:,1], 60, 255, cv2.THRESH_BINARY_INV)
	
	blur_image = cv2.GaussianBlur(threshed, (7,7), 0)

	#print(blur_image)

	# Find edges
	sobel_x = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 1, 0, 7))
	sobel_y = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 0, 1, 7))	
	
	sobel = (sobel_x ** 2 + sobel_y ** 2)**1/2

	sobel_image = np.ones_like(sobel, dtype=blur_image.dtype)
	sobel_image[(sobel <= 30)] = 0
	
	#s_channel = cvt_image[ :, :, 2]
	##TEST
	'''
	_, s_binary = cv2.threshold(cvt_image[:, :, 2], 110, 255, cv2.THRESH_BINARY_INV)
	_, r_thresh = cv2.threshold(ori[:,:,2], 70, 255, cv2.THRESH_BINARY)
	_binary = cv2.bitwise_and(s_binary, r_thresh)
	blur_image = cv2.GaussianBlur(_binary, (7,7), 0)
	sobel_x = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 1, 0, 3))
	sobel_y = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 0, 1, 3))
	sobel = (sobel_x ** 2 + sobel_y ** 2)**1/2
	sobel_image = np.ones_like(sobel, dtype=blur_image.dtype)
	sobel_image[(sobel >= 110) & (sobel <= 255)] = 0
	'''
	##TEST
	
	_, s_binary = cv2.threshold(cvt_image[:, :, 2], 110, 255, cv2.THRESH_BINARY_INV)
	_, r_thresh = cv2.threshold(ori[:,:,2], 70, 255, cv2.THRESH_BINARY)
	_binary = cv2.bitwise_and(s_binary, r_thresh)
	mask_maybe = cv2.bitwise_or(_binary, sobel_image.astype(np.uint8))
	

	#print(sobel_image)
	
	print()
	# Print result
	imageArray = np.array(image)
	imageArray[sobel_image == 1] = np.array([0, 255, 0])
	
	imageArray = cv2.addWeighted(imageArray, 0.5, ori, 1, 0)
	
	#print(result, type(result))
	
	
	print(cv2.threshold(cvt_image[:,:,1], 130, 255, cv2.THRESH_BINARY_INV))

	threshold = 50

	#h_img = cv2.cvtColor(cv2.threshold(cvt_image[:,:,0], threshold, 255, cv2.THRESH_BINARY_INV)[1], cv2.COLOR_GRAY2RGB)
	#l_img = cv2.cvtColor(cv2.threshold(cvt_image[:,:,1], threshold, 255, cv2.THRESH_BINARY_INV)[1], cv2.COLOR_GRAY2RGB)
	#s_img = cv2.cvtColor(cv2.threshold(cvt_image[:,:,2], threshold, 255, cv2.THRESH_BINARY_INV)[1], cv2.COLOR_GRAY2RGB)
	
	h_img = cv2.cvtColor(cvt_image[:,:,0], cv2.COLOR_GRAY2RGB)
	l_img = cv2.cvtColor(cvt_image[:,:,1], cv2.COLOR_GRAY2RGB)
	s_img = cv2.cvtColor(cvt_image[:,:,2], cv2.COLOR_GRAY2RGB)

	print(h_img)
	
	final = np.concatenate((np.concatenate((h_img, s_img), axis=1), np.concatenate((l_img, imageArray), axis=1)))
	
	im_name = "¡YEAY!"
	cv2.namedWindow(im_name, cv2.WINDOW_NORMAL)
	cv2.resizeWindow(im_name, 1500, 800)
	cv2.imshow(im_name, final)# imageArray)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	





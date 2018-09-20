from django.conf.urls import url
from views import upload_celebrity_details, fetch_celebrity_details, save_celebrity_schedules, \
    fetch_celebrity_schedules, save_public_suggestion, publish_public_suggestions, get_public_suggestions, \
    fetch_carousel_images, get_all_public_suggestions, login, logout, register, upload_carousel_images, \
    save_mobile_token, check_login, fetch_social_id, save_social_id,delete_image, delete_celebrity_details, \
    delete_celebrity_video, change_password, mail_confirmation, checkcurrentpassword, update_celebrity_details, \
    delete_schedule, delete_public_suggestion, message_notification ,set_default_price, set_custom_price, search_dates, \
    show_prices, book_Now, updateCustomPrice, deletePrice, blockDates, blockeddates, deleteblockeddates, bookingdetails, \
    getbookings, getDates, getDates2, getcategory, savecategory

urlpatterns = [
    url(r'^upload_celebrity_details/$', upload_celebrity_details),
    url(r'^fetch_celebrity_details/$', fetch_celebrity_details),
    url(r'^save_celebrity_schedules/$', save_celebrity_schedules),
    url(r'^fetch_celebrity_schedules/$', fetch_celebrity_schedules),
    url(r'^save_public_suggestion/$', save_public_suggestion),
    url(r'^publish_public_suggestions/$', publish_public_suggestions),
    url(r'^get_all_public_suggestions/$', get_all_public_suggestions),
    url(r'^get_public_suggestions/$', get_public_suggestions),
    url(r'^fetch_carousel_images/$', fetch_carousel_images),
    url(r'^login/$', login),
    url(r'^logout/$', logout),
    url(r'^register/$', register),
    url(r'^upload_carousel_images/$', upload_carousel_images),
    url(r'^save_mobile_token/$', save_mobile_token),
    url(r'^check_login/$', check_login),
    url(r'^fetch_social_id/$', fetch_social_id),
    url(r'^save_social_id/$', save_social_id),
    url(r'^deleteimage/$', delete_image),
    url(r'^biography/$', delete_celebrity_details),
    url(r'^video/$', delete_celebrity_video),
    url(r'^change_password', change_password),
    url(r'^mailconfirmation', mail_confirmation),
    url(r'^checkcurrentpassword', checkcurrentpassword),
    url(r'^update_celebrity_details/$',update_celebrity_details),
    url(r'^delete_schedule/$', delete_schedule),
    url(r'^delete_public_suggestion', delete_public_suggestion),
    url(r'^message_notification/$', message_notification),
    url(r'^set_defaultprice/$', set_default_price),
    url(r'^set_customprice/$', set_custom_price),
    url(r'^search_dates/$', search_dates),
    url(r'^showPrice/$', show_prices),
    url(r'^book_now',book_Now),
    url(r'^updateCustomPrice/$', updateCustomPrice),
    url(r'^deletePrice/$', deletePrice),
    url(r'^blockDates/$', blockDates),
    url(r'^blockeddates/$', blockeddates),
    url(r'^deleteblockeddates/$', deleteblockeddates),
    url(r'^bookingdetails/$', bookingdetails),
    url(r'^getbookings/$', getbookings),
    url(r'^getDates/$', getDates),
    url(r'^getDates2/$', getDates2),
    url(r'^getcategory/$', getcategory),
    url(r'^savecategory/$', savecategory)

]

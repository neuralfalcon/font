from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from datetime import datetime
from IPython.display import clear_output

# Sample comment data
comment_data = {
    'text': 'i purchased realme gt2',
    'author_display_name': 'afdhhadfh',
    'author_profile_image_url': 'https://yt3.ggpht.com/afadhadf=s48-c-k-c0x00ffffff-no-rj',
    'comment_id': 'ahahaafh',
    'published_at': '2023-07-29T18:10:56Z',
    'likeCount': 5,  # Change the value to test different cases (0 or greater than 0)
    'totalReplyCount': 5,  # Change the value to test different cases (0, 1, or greater than 1)
}

# Font paths (replace with your own font files)
font_path_regular = '/content/Roboto-Regular.ttf'
font_path_bold = '/content/Roboto-Bold.ttf'
font_path_thin = '/content/Roboto-Thin.ttf'  # Add the font path for Roboto-Thin.ttf

# Load the profile image using requests
response = requests.get(comment_data['author_profile_image_url'])
profile_image = Image.open(BytesIO(response.content)).convert("RGBA")

# Calculate the dimensions for the final image
width, height = 600, 200  # Increased height to accommodate "like.jpg", "reply.jpg", and "down.jpg" images
profile_size = 80  # Make the profile image smaller

# Create a blank RGBA image with a white background
image = Image.new('RGBA', (width, height), color='white')

# Create a circular mask for the profile picture
mask = Image.new('L', (profile_size, profile_size), 0)
draw_mask = ImageDraw.Draw(mask)
draw_mask.ellipse((0, 0, profile_size, profile_size), fill=255)

# Resize and crop the profile image to match the desired circular shape
profile_image_resized = profile_image.resize((profile_size, profile_size), Image.LANCZOS).convert('RGBA')
circular_profile_image = Image.new('RGBA', (profile_size, profile_size), (255, 255, 255, 0))
circular_profile_image.paste(profile_image_resized, (0, 0), mask=mask)

# Paste the circular-profile image onto the blank image
image.paste(circular_profile_image, (10, 10), circular_profile_image)

# Draw the username and comment text on the image
draw = ImageDraw.Draw(image)

# Load the fonts (replace size with your desired font size)
font_username = ImageFont.truetype(font_path_bold, size=18)
font_comment = ImageFont.truetype(font_path_regular, size=20)  # Increase font size to 20
font_like_thin = ImageFont.truetype(font_path_thin, size=20)  # Specify the font for "like" count

username = ' @' + comment_data['author_display_name']
x_username, y_username = profile_size + 20, 15
draw.text((x_username, y_username), username, fill='black', font=font_username)

# Add the timestamp after the username
timestamp_str = ""
try:
    comment_timestamp = datetime.strptime(comment_data['published_at'], '%Y-%m-%dT%H:%M:%SZ')
    time_ago = datetime.utcnow() - comment_timestamp

    days_ago = int(time_ago.total_seconds() // (3600 * 24))
    hours_ago = int((time_ago.total_seconds() % (3600 * 24)) // 3600)
    minutes_ago = int((time_ago.total_seconds() % 3600) // 60)
    seconds_ago = int(time_ago.total_seconds() % 60)

    if days_ago > 0:
        timestamp_str = f"{days_ago} days ago"
    elif hours_ago > 0:
        timestamp_str = f"{hours_ago} hr ago"
    elif minutes_ago > 0:
        timestamp_str = f"{minutes_ago} min ago"
    else:
        timestamp_str = f"{seconds_ago} sec ago"
except ValueError:
    timestamp_str = ""

x_timestamp, y_timestamp = x_username + draw.textsize(username, font=font_username)[0] + 10, y_username
draw.text((x_timestamp, y_timestamp), timestamp_str, fill='black', font=font_username)

comment = comment_data['text']
x_comment, y_comment = x_username, y_username + font_username.getsize(username)[1] + 10  # Increase y offset for comment
max_comment_width = width - profile_size - 30
comment_lines = []
current_line = ' '
for word in comment.split():
    new_line = current_line + word + ' '
    if draw.textsize(new_line, font=font_comment)[0] <= max_comment_width:
        current_line = new_line
    else:
        comment_lines.append(current_line)
        current_line = word + ' '
comment_lines.append(current_line)
for i, line in enumerate(comment_lines):
    draw.text((x_comment, y_comment + i * font_comment.getsize(line)[1]), line, fill='black', font=font_comment)

# Load the "like.jpg", "reply.jpg", and "down.jpg" images
like_image_path = '/content/like.jpg'  # Replace with the actual path of the "like.jpg" image
reply_image_path = '/content/reply.jpg'  # Replace with the actual path of the "reply.jpg" image
down_image_path = '/content/down.jpg'    # Replace with the actual path of the "down.jpg" image

like_image = Image.open(like_image_path)
reply_image = Image.open(reply_image_path)
down_image = Image.open(down_image_path)

# Calculate the position for the "like.jpg", "reply.jpg", and "down.jpg" images
like_width, like_height = 30, 30
reply_width, reply_height = 30, 30
down_width, down_height = 30, 30

x_like, y_like = x_comment, y_comment + font_comment.getsize(comment)[1] + 10

# Check if the likeCount is greater than 0 and display the number of likes
if comment_data['likeCount'] > 0:
    likes_text = f"{comment_data['likeCount']} "
    x_likes_text, y_likes_text = x_like + like_width + 5, y_like + 12
    draw.text((x_likes_text, y_likes_text), likes_text, fill='black', font=font_like_thin)
    x_reply, y_reply = x_likes_text + draw.textsize(likes_text, font=font_like_thin)[0] + 5, y_like
else:
    likes_text = f" "
    x_likes_text, y_likes_text = x_like + like_width + 5, y_like + 12
    draw.text((x_likes_text, y_likes_text), likes_text, fill='black', font=font_like_thin)
    x_reply, y_reply = x_likes_text + draw.textsize(likes_text, font=font_like_thin)[0] + 5, y_like

# Paste the "like.jpg" and "reply.jpg" images onto the image canvas
image.paste(like_image, (x_like, y_like))
image.paste(reply_image, (x_reply, y_reply))

# Check if totalReplyCount is greater than 1 and display "down.jpg" image and the total reply count
if comment_data['totalReplyCount'] > 1:
    x_down, y_down = x_like, y_like + like_height + 10
    image.paste(down_image, (x_down+2, y_down))
    total_reply_count_text = f"{comment_data['totalReplyCount']} replies"
    x_total_reply_count, y_total_reply_count = x_down + down_width + 5, y_down + 12

    # Load the font for the total reply count text (use font_path_bold)
    font_total_reply_count = ImageFont.truetype(font_path_bold, size=20)
    
    draw.text((x_total_reply_count, y_total_reply_count), total_reply_count_text, fill='#1465D7', font=font_total_reply_count)

# Save the final image
image_path = 'youtube_comment.png'
image.save(image_path)

# Optionally, you can display the image using PIL
clear_output()
image






from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from datetime import datetime
from IPython.display import clear_output
# Font paths (replace with your own font files)
font_path_regular = '/content/Roboto-Regular.ttf'
font_path_bold = '/content/Roboto-Bold.ttf'
font_path_thin = '/content/Roboto-Thin.ttf'  # Add the font path for Roboto-Thin.ttf
# Load the "like.jpg", "reply.jpg", and "down.jpg" images
like_image_path = '/content/like.jpg'  # Replace with the actual path of the "like.jpg" image
reply_image_path = '/content/reply.jpg'  # Replace with the actual path of the "reply.jpg" image
down_image_path = '/content/down.jpg'    # Replace with the actual path of the "down.jpg" image

like_image = Image.open(like_image_path)
reply_image = Image.open(reply_image_path)
down_image = Image.open(down_image_path)
def generate_comment_screenshot(comment_data,save_path):
  # Load the profile image using requests
  response = requests.get(comment_data['author_profile_image_url'])
  profile_image = Image.open(BytesIO(response.content)).convert("RGBA")

  # Calculate the dimensions for the final image
  width, height = 600, 200  # Increased height to accommodate "like.jpg", "reply.jpg", and "down.jpg" images
  profile_size = 80  # Make the profile image smaller

  # Create a blank RGBA image with a white background
  image = Image.new('RGBA', (width, height), color='white')

  # Create a circular mask for the profile picture
  mask = Image.new('L', (profile_size, profile_size), 0)
  draw_mask = ImageDraw.Draw(mask)
  draw_mask.ellipse((0, 0, profile_size, profile_size), fill=255)

  # Resize and crop the profile image to match the desired circular shape
  profile_image_resized = profile_image.resize((profile_size, profile_size), Image.LANCZOS).convert('RGBA')
  circular_profile_image = Image.new('RGBA', (profile_size, profile_size), (255, 255, 255, 0))
  circular_profile_image.paste(profile_image_resized, (0, 0), mask=mask)

  # Paste the circular-profile image onto the blank image
  image.paste(circular_profile_image, (10, 10), circular_profile_image)

  # Draw the username and comment text on the image
  draw = ImageDraw.Draw(image)

  # Load the fonts (replace size with your desired font size)
  font_username = ImageFont.truetype(font_path_bold, size=18)
  font_comment = ImageFont.truetype(font_path_regular, size=20)  # Increase font size to 20
  font_like_thin = ImageFont.truetype(font_path_thin, size=20)  # Specify the font for "like" count

  username = ' @' + comment_data['author_display_name']
  x_username, y_username = profile_size + 20, 15
  draw.text((x_username, y_username), username, fill='black', font=font_username)

  # Add the timestamp after the username
  timestamp_str = ""
  try:
      comment_timestamp = datetime.strptime(comment_data['published_at'], '%Y-%m-%dT%H:%M:%SZ')
      time_ago = datetime.utcnow() - comment_timestamp

      days_ago = int(time_ago.total_seconds() // (3600 * 24))
      hours_ago = int((time_ago.total_seconds() % (3600 * 24)) // 3600)
      minutes_ago = int((time_ago.total_seconds() % 3600) // 60)
      seconds_ago = int(time_ago.total_seconds() % 60)

      if days_ago > 0:
          timestamp_str = f"{days_ago} days ago"
      elif hours_ago > 0:
          timestamp_str = f"{hours_ago} hr ago"
      elif minutes_ago > 0:
          timestamp_str = f"{minutes_ago} min ago"
      else:
          timestamp_str = f"{seconds_ago} sec ago"
  except ValueError:
      timestamp_str = ""

  x_timestamp, y_timestamp = x_username + draw.textsize(username, font=font_username)[0] + 10, y_username
  draw.text((x_timestamp, y_timestamp), timestamp_str, fill='black', font=font_username)

  comment = comment_data['text']
  x_comment, y_comment = x_username, y_username + font_username.getsize(username)[1] + 10  # Increase y offset for comment
  max_comment_width = width - profile_size - 30
  comment_lines = []
  current_line = ' '
  for word in comment.split():
      new_line = current_line + word + ' '
      if draw.textsize(new_line, font=font_comment)[0] <= max_comment_width:
          current_line = new_line
      else:
          comment_lines.append(current_line)
          current_line = word + ' '
  comment_lines.append(current_line)
  for i, line in enumerate(comment_lines):
      draw.text((x_comment, y_comment + i * font_comment.getsize(line)[1]), line, fill='black', font=font_comment)



  # Calculate the position for the "like.jpg", "reply.jpg", and "down.jpg" images
  like_width, like_height = 30, 30
  reply_width, reply_height = 30, 30
  down_width, down_height = 30, 30

  x_like, y_like = x_comment, y_comment + font_comment.getsize(comment)[1] + 10

  # Check if the likeCount is greater than 0 and display the number of likes
  if comment_data['likeCount'] > 0:
      likes_text = f"{comment_data['likeCount']} "
      x_likes_text, y_likes_text = x_like + like_width + 5, y_like + 12
      draw.text((x_likes_text, y_likes_text), likes_text, fill='black', font=font_like_thin)
      x_reply, y_reply = x_likes_text + draw.textsize(likes_text, font=font_like_thin)[0] + 5, y_like
  else:
      likes_text = f" "
      x_likes_text, y_likes_text = x_like + like_width + 5, y_like + 12
      draw.text((x_likes_text, y_likes_text), likes_text, fill='black', font=font_like_thin)
      x_reply, y_reply = x_likes_text + draw.textsize(likes_text, font=font_like_thin)[0] + 5, y_like

  # Paste the "like.jpg" and "reply.jpg" images onto the image canvas
  image.paste(like_image, (x_like, y_like))
  image.paste(reply_image, (x_reply, y_reply))

  # Check if totalReplyCount is greater than 1 and display "down.jpg" image and the total reply count
  if comment_data['totalReplyCount'] > 1:
      x_down, y_down = x_like, y_like + like_height + 10
      image.paste(down_image, (x_down+2, y_down))
      total_reply_count_text = f"{comment_data['totalReplyCount']} replies"
      x_total_reply_count, y_total_reply_count = x_down + down_width + 5, y_down + 12

      # Load the font for the total reply count text (use font_path_bold)
      font_total_reply_count = ImageFont.truetype(font_path_bold, size=20)
      
      draw.text((x_total_reply_count, y_total_reply_count), total_reply_count_text, fill='#1465D7', font=font_total_reply_count)

  # Save the final image
  image_path = save_path
  image.save(image_path)

  # Optionally, you can display the image using PIL
  clear_output()
  return image


# Sample comment data
comment_data = {
    'text': 'i purchased realme gt2',
    'author_display_name': 'Shivendra Mishra',
    'author_profile_image_url': 'https://yt3.ggpht.com/1brrhFzIQm3I4B0I1RjqXWKpcA6c3i9u7zlT61EGzBuQZurPMECFmNNG5Q6K7gu74OIHGiUG=s48-c-k-c0x00ffffff-no-rj',
    'comment_id': 'Ugwz7Yflo7YZOepLWB94AaABAg',
    'published_at': '2023-07-29T18:10:56Z',
    'likeCount': 5,  # Change the value to test different cases (0 or greater than 0)
    'totalReplyCount': 5,  # Change the value to test different cases (0, 1, or greater than 1)
}

generate_comment_screenshot(comment_data,"demo.png")

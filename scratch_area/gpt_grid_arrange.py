import random
from typing import List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def arrange_images(
    images: List[Tuple[int, int, int]], max_width: int
) -> List[Tuple[int, int, int, int, int]]:
    # Sort images by ID (assuming the input is unsorted)
    images.sort(key=lambda x: x[2])

    arranged = []
    current_x, current_y = 0, 0
    row_height = 0

    for width, height, img_id in images:
        aspect_ratio = width / height

        # Resize image if it would exceed the max width
        if current_x + width > max_width:
            # Move to the next row
            current_y += row_height
            current_x = 0
            row_height = 0

        # Ensure the image fits within the remaining space in the row
        if current_x + width > max_width:
            width = max_width - current_x
            height = int(width / aspect_ratio)

        # Update row height if this image is taller
        row_height = max(row_height, height)

        # Add the image with its new position to the arranged list
        arranged.append((width, height, current_x, current_y, img_id))

        # Move x position for the next image
        current_x += width

    return arranged


# Example Usage:
images = []
for n in range(50):
    images.append((random.randrange(256, 2048, 64), random.randrange(256, 2048, 64), n))
max_width = 500
arranged_images = arrange_images(images, max_width)
print(arranged_images)


def visualize_image_arrangement(
    arranged_images: List[Tuple[int, int, int, int, int]], max_width: int
):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 10)
    fig.set_dpi(fig.get_dpi() * 8)
    for width, height, x, y, img_id in arranged_images:
        # Draw a rectangle representing the image
        rect = patches.Rectangle(
            (x, y),
            width,
            height,
            linewidth=1,
            edgecolor="blue",
            facecolor="cyan",
            alpha=0.5,
        )
        ax.add_patch(rect)
        # Label the rectangle with its ID
        ax.text(
            x + width / 2,
            y + height / 2,
            f"{width:.2f} {height:.2f} {x:.2f} {y:.2f} {img_id}",
            fontsize=12,
            ha="center",
            va="center",
        )

    # Set limits and labels
    ax.set_xlim(0, max_width)
    ax.set_ylim(0, max([y + height for _, height, _, y, _ in arranged_images]))
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Image Arrangement Visualization")
    ax.invert_yaxis()  # Invert y-axis to match the typical coordinate system
    fig.savefig("./out.png")
    # plt.show()


# Visualize the arrangement
visualize_image_arrangement(arranged_images, max_width)

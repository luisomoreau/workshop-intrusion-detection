# Intrusion Detection Workshop

![gif](templates/assets/render.gif)

## Edge Impulse Public Project

[https://studio.edgeimpulse.com/public/40479/latest](https://studio.edgeimpulse.com/public/40479/latest)

## Build your dataset

### Collecting your own images



### Bounding Boxes format

If you want to upload data for object detection, the uploader can label the data for you as it uploads it. In order to do this, all you need is to create a bounding_boxes.labels file **in the same folder as your image files**. The contents of this file are formatted as JSON with the following structure:

```
{
    "version": 1,
    "type": "bounding-box-labels",
    "boundingBoxes": {
        "mypicture.jpg": [{
            "label": "person",
            "x": 119,
            "y": 64,
            "width": 206,
            "height": 291
        }, {
            "label": "person",
            "x": 377,
            "y": 270,
            "width": 158,
            "height": 165
        }]
    }
}
```

```yaml
config:
- feature1:
    key: value
    keys:
      - value1
      - value2
  feature2:
    key: value
    keys:
      - value1
      - value2

same

---
- config:
    feature1:
      key: value
      keys:
        - value1
        - value2
    feature2:
      key: value
      keys:
        - value1
        - value2
```
{ config: [ { feature1: [Object], feature2: [Object] } ] }

```yaml
- feature1:
    key: value
    keys:
      - value1
      - value2
  feature2:
    key: value
    keys:
      - value1
      - value2

- feature1:
    key: value
    keys:
      - value1
      - value2
- feature2:
    key: value
    keys:
      - value1
      - value2
```
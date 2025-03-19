Docker CMD:
```sh
docker run -it --rm -e GOOGLE_API_KEY=your_api_key  -v .:/app/images ai-nutrition-fact-checker get_nf_from_image      
docker run -it --rm -e GOOGLE_API_KEY=your_api_key  ai-nutrition-fact-checker get_nf_from_product_info --product_Name "Oats" --company_name "Quaker" --description "Whole grain oats with no added sugar"                   

```

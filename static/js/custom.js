window.addEventListener("load", () => {
  const btnAddToCart = document.querySelectorAll(".add-to-cart");
  const qtyOfCart = document.querySelector(".cart-qty");
  const cartPrice = document.querySelector(".cartTotalPrice");
  const cartContent = document.querySelector(".headerTopCartDropdownContent");
  let btnCartCounter = document.querySelectorAll(".btn-cart-counter");

  const updateCart = (data) => {
    const cart = data["data"]["cart"];
    cartContent.firstElementChild.innerHTML = "";
    let cartHTMLContent = "";
    cart["items"] &&
      cart["items"].forEach((item) => {
        if (item.pic === null) {
          item.pic = "/static/img/products/placeholder.jpg";
        }
        cartHTMLContent += `
        <li class="item">
            <a href="#" title="${item.title}" class="product-image"><img
                    src="${item.pic}"
                    alt="${item.title}"></a>
            <div class="product-details">
                <p class="product-name">
                    <a href="#">${item.title}</a>
                </p>
                <p class="qty-price mb-1">
                    (${item.count} عدد) <span class="price">${Number(
          Number(item.total)
        ).toLocaleString()} تومان</span>
                </p>
                <div class="d-flex justify-content-end">
                <button class="btn btn-primary btn-sm text-white btn-cart-counter" data-prod="${
                  item.id
                }" data-flag="1"><i class="fa fa-plus"></i>
                </button>
                <button class="btn btn-primary btn-sm text-white me-2 btn-cart-counter" data-prod="${
                  item.id
                }" data-flag="0"><i class="fa fa-minus"></i>
											</button>
                </div>
                
            </div>
        </li>
        `;
      });

    qtyOfCart.innerText = cart["items"] ? cart["items"].length : 0;
    cartContent.firstElementChild.innerHTML = cartHTMLContent;
    cartPrice.innerText = cart["total"]
      ? Number(Number(cart["total"])).toLocaleString()
      : 0;

    btnCartCounter = document.querySelectorAll(".btn-cart-counter");
    btnCartCounter.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();

        //   updating the page ...
        fetch(`/api/cart/${btn.dataset.flag}/${btn.dataset.prod}/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        })
          .then((response) => response.json())
          .then((data) => {
            updateCart(data);
          });
      });
    });
  };

  //   first loading the page ...
  fetch(`/api/cart/${0}/${0}/`)
    .then((response) => response.json())
    .then((data) => {
      updateCart(data);
    });

  btnAddToCart.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();

      //   updating the page ...
      fetch(`/api/cart/${1}/${btn.dataset.prod}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      })
        .then((response) => response.json())
        .then((data) => {
          updateCart(data);
        });
    });
  });
});

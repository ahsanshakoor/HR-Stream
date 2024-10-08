/**
 * @popperjs/core v2.8.4 - MIT License
 */

(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
    typeof define === 'function' && define.amd ? define(['exports'], factory) :
      (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.Popper = {}));
}(this, (function (exports) {
  'use strict';

  function getBoundingClientRect(element) {
    var rect = element.getBoundingClientRect();
    return {
      width: rect.width,
      height: rect.height,
      top: rect.top,
      right: rect.right,
      bottom: rect.bottom,
      left: rect.left,
      x: rect.left,
      y: rect.top
    };
  }

  /*:: import type { Window } from '../types'; */

  /*:: declare function getWindow(node: Node | Window): Window; */
  function getWindow(node) {
    if (node.toString() !== '[object Window]') {
      var ownerDocument = node.ownerDocument;
      return ownerDocument ? ownerDocument.defaultView || window : window;
    }

    return node;
  }

  function getWindowScroll(node) {
    var win = getWindow(node);
    var scrollLeft = win.pageXOffset;
    var scrollTop = win.pageYOffset;
    return {
      scrollLeft: scrollLeft,
      scrollTop: scrollTop
    };
  }

  /*:: declare function isElement(node: mixed): boolean %checks(node instanceof
    Element); */

  function isElement(node) {
    var OwnElement = getWindow(node).Element;
    return node instanceof OwnElement || node instanceof Element;
  }
  /*:: declare function isHTMLElement(node: mixed): boolean %checks(node instanceof
    HTMLElement); */


  function isHTMLElement(node) {
    var OwnElement = getWindow(node).HTMLElement;
    return node instanceof OwnElement || node instanceof HTMLElement;
  }
  /*:: declare function isShadowRoot(node: mixed): boolean %checks(node instanceof
    ShadowRoot); */


  function isShadowRoot(node) {
    // IE 11 has no ShadowRoot
    if (typeof ShadowRoot === 'undefined') {
      return false;
    }

    var OwnElement = getWindow(node).ShadowRoot;
    return node instanceof OwnElement || node instanceof ShadowRoot;
  }

  function getHTMLElementScroll(element) {
    return {
      scrollLeft: element.scrollLeft,
      scrollTop: element.scrollTop
    };
  }

  function getNodeScroll(node) {
    if (node === getWindow(node) || !isHTMLElement(node)) {
      return getWindowScroll(node);
    } else {
      return getHTMLElementScroll(node);
    }
  }

  function getNodeName(element) {
    return element ? (element.nodeName || '').toLowerCase() : null;
  }

  function getDocumentElement(element) {
    // $FlowFixMe[incompatible-return]: assume body is always available
    return ((isElement(element) ? element.ownerDocument : // $FlowFixMe[prop-missing]
      element.document) || window.document).documentElement;
  }

  function getWindowScrollBarX(element) {
    // If <html> has a CSS width greater than the viewport, then this will be
    // incorrect for RTL.
    // Popper 1 is broken in this case and never had a bug report so let's assume
    // it's not an issue. I don't think anyone ever specifies width on <html>
    // anyway.
    // Browsers where the left scrollbar doesn't cause an issue report `0` for
    // this (e.g. Edge 2019, IE11, Safari)
    return getBoundingClientRect(getDocumentElement(element)).left + getWindowScroll(element).scrollLeft;
  }

  function getComputedStyle(element) {
    return getWindow(element).getComputedStyle(element);
  }

  function isScrollParent(element) {
    // Firefox wants us to check `-x` and `-y` variations as well
    var _getComputedStyle = getComputedStyle(element),
      overflow = _getComputedStyle.overflow,
      overflowX = _getComputedStyle.overflowX,
      overflowY = _getComputedStyle.overflowY;

    return /auto|scroll|overlay|hidden/.test(overflow + overflowY + overflowX);
  }

  // Composite means it takes into account transforms as well as layout.

  function getCompositeRect(elementOrVirtualElement, offsetParent, isFixed) {
    if (isFixed === void 0) {
      isFixed = false;
    }

    var documentElement = getDocumentElement(offsetParent);
    var rect = getBoundingClientRect(elementOrVirtualElement);
    var isOffsetParentAnElement = isHTMLElement(offsetParent);
    var scroll = {
      scrollLeft: 0,
      scrollTop: 0
    };
    var offsets = {
      x: 0,
      y: 0
    };

    if (isOffsetParentAnElement || !isOffsetParentAnElement && !isFixed) {
      if (getNodeName(offsetParent) !== 'body' || // https://github.com/popperjs/popper-core/issues/1078
        isScrollParent(documentElement)) {
        scroll = getNodeScroll(offsetParent);
      }

      if (isHTMLElement(offsetParent)) {
        offsets = getBoundingClientRect(offsetParent);
        offsets.x += offsetParent.clientLeft;
        offsets.y += offsetParent.clientTop;
      } else if (documentElement) {
        offsets.x = getWindowScrollBarX(documentElement);
      }
    }

    return {
      x: rect.left + scroll.scrollLeft - offsets.x,
      y: rect.top + scroll.scrollTop - offsets.y,
      width: rect.width,
      height: rect.height
    };
  }

  // Returns the layout rect of an element relative to its offsetParent. Layout
  // means it doesn't take into account transforms.
  function getLayoutRect(element) {
    return {
      x: element.offsetLeft,
      y: element.offsetTop,
      width: element.offsetWidth,
      height: element.offsetHeight
    };
  }

  function getParentNode(element) {
    if (getNodeName(element) === 'html') {
      return element;
    }

    return (// this is a quicker (but less type safe) way to save quite some bytes from the bundle
      // $FlowFixMe[incompatible-return]
      // $FlowFixMe[prop-missing]
      element.assignedSlot || // step into the shadow DOM of the parent of a slotted node
      element.parentNode || ( // DOM Element detected
        isShadowRoot(element) ? element.host : null) || // ShadowRoot detected
      // $FlowFixMe[incompatible-call]: HTMLElement is a Node
      getDocumentElement(element) // fallback

    );
  }

  function getScrollParent(node) {
    if (['html', 'body', '#document'].indexOf(getNodeName(node)) >= 0) {
      // $FlowFixMe[incompatible-return]: assume body is always available
      return node.ownerDocument.body;
    }

    if (isHTMLElement(node) && isScrollParent(node)) {
      return node;
    }

    return getScrollParent(getParentNode(node));
  }

  /*
  given a DOM element, return the list of all scroll parents, up the list of ancesors
  until we get to the top window object. This list is what we attach scroll listeners
  to, because if any of these parent elements scroll, we'll need to re-calculate the
  reference element's position.
  */

  function listScrollParents(element, list) {
    var _element$ownerDocumen;

    if (list === void 0) {
      list = [];
    }

    var scrollParent = getScrollParent(element);
    var isBody = scrollParent === ((_element$ownerDocumen = element.ownerDocument) == null ? void 0 : _element$ownerDocumen.body);
    var win = getWindow(scrollParent);
    var target = isBody ? [win].concat(win.visualViewport || [], isScrollParent(scrollParent) ? scrollParent : []) : scrollParent;
    var updatedList = list.concat(target);
    return isBody ? updatedList : // $FlowFixMe[incompatible-call]: isBody tells us target will be an HTMLElement here
      updatedList.concat(listScrollParents(getParentNode(target)));
  }

  function isTableElement(element) {
    return ['table', 'td', 'th'].indexOf(getNodeName(element)) >= 0;
  }

  function getTrueOffsetParent(element) {
    if (!isHTMLElement(element) || // https://github.com/popperjs/popper-core/issues/837
      getComputedStyle(element).position === 'fixed') {
      return null;
    }

    return element.offsetParent;
  } // `.offsetParent` reports `null` for fixed elements, while absolute elements
  // return the containing block


  function getContainingBlock(element) {
    var isFirefox = navigator.userAgent.toLowerCase().includes('firefox');
    var currentNode = getParentNode(element);

    while (isHTMLElement(currentNode) && ['html', 'body'].indexOf(getNodeName(currentNode)) < 0) {
      var css = getComputedStyle(currentNode); // This is non-exhaustive but covers the most common CSS properties that
      // create a containing block.
      // https://developer.mozilla.org/en-US/docs/Web/CSS/Containing_block#identifying_the_containing_block

      if (css.transform !== 'none' || css.perspective !== 'none' || css.contain === 'paint' || ['transform', 'perspective'].includes(css.willChange) || isFirefox && css.willChange === 'filter' || isFirefox && css.filter && css.filter !== 'none') {
        return currentNode;
      } else {
        currentNode = currentNode.parentNode;
      }
    }

    return null;
  } // Gets the closest ancestor positioned element. Handles some edge cases,
  // such as table ancestors and cross browser bugs.


  function getOffsetParent(element) {
    var window = getWindow(element);
    var offsetParent = getTrueOffsetParent(element);

    while (offsetParent && isTableElement(offsetParent) && getComputedStyle(offsetParent).position === 'static') {
      offsetParent = getTrueOffsetParent(offsetParent);
    }

    if (offsetParent && (getNodeName(offsetParent) === 'html' || getNodeName(offsetParent) === 'body' && getComputedStyle(offsetParent).position === 'static')) {
      return window;
    }

    return offsetParent || getContainingBlock(element) || window;
  }

  var top = 'top';
  var bottom = 'bottom';
  var right = 'right';
  var left = 'left';
  var auto = 'auto';
  var basePlacements = [top, bottom, right, left];
  var start = 'start';
  var end = 'end';
  var clippingParents = 'clippingParents';
  var viewport = 'viewport';
  var popper = 'popper';
  var reference = 'reference';
  var variationPlacements = /*#__PURE__*/basePlacements.reduce(function (acc, placement) {
    return acc.concat([placement + "-" + start, placement + "-" + end]);
  }, []);
  var placements = /*#__PURE__*/[].concat(basePlacements, [auto]).reduce(function (acc, placement) {
    return acc.concat([placement, placement + "-" + start, placement + "-" + end]);
  }, []); // modifiers that need to read the DOM

  var beforeRead = 'beforeRead';
  var read = 'read';
  var afterRead = 'afterRead'; // pure-logic modifiers

  var beforeMain = 'beforeMain';
  var main = 'main';
  var afterMain = 'afterMain'; // modifier with the purpose to write to the DOM (or write into a framework state)

  var beforeWrite = 'beforeWrite';
  var write = 'write';
  var afterWrite = 'afterWrite';
  var modifierPhases = [beforeRead, read, afterRead, beforeMain, main, afterMain, beforeWrite, write, afterWrite];

  function order(modifiers) {
    var map = new Map();
    var visited = new Set();
    var result = [];
    modifiers.forEach(function (modifier) {
      map.set(modifier.name, modifier);
    }); // On visiting object, check for its dependencies and visit them recursively

    function sort(modifier) {
      visited.add(modifier.name);
      var requires = [].concat(modifier.requires || [], modifier.requiresIfExists || []);
      requires.forEach(function (dep) {
        if (!visited.has(dep)) {
          var depModifier = map.get(dep);

          if (depModifier) {
            sort(depModifier);
          }
        }
      });
      result.push(modifier);
    }

    modifiers.forEach(function (modifier) {
      if (!visited.has(modifier.name)) {
        // check for visited object
        sort(modifier);
      }
    });
    return result;
  }

  function orderModifiers(modifiers) {
    // order based on dependencies
    var orderedModifiers = order(modifiers); // order based on phase

    return modifierPhases.reduce(function (acc, phase) {
      return acc.concat(orderedModifiers.filter(function (modifier) {
        return modifier.phase === phase;
      }));
    }, []);
  }

  function debounce(fn) {
    var pending;
    return function () {
      if (!pending) {
        pending = new Promise(function (resolve) {
          Promise.resolve().then(function () {
            pending = undefined;
            resolve(fn());
          });
        });
      }

      return pending;
    };
  }

  function format(str) {
    for (var _len = arguments.length, args = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
      args[_key - 1] = arguments[_key];
    }

    return [].concat(args).reduce(function (p, c) {
      return p.replace(/%s/, c);
    }, str);
  }

  var INVALID_MODIFIER_ERROR = 'Popper: modifier "%s" provided an invalid %s property, expected %s but got %s';
  var MISSING_DEPENDENCY_ERROR = 'Popper: modifier "%s" requires "%s", but "%s" modifier is not available';
  var VALID_PROPERTIES = ['name', 'enabled', 'phase', 'fn', 'effect', 'requires', 'options'];
  function validateModifiers(modifiers) {
    modifiers.forEach(function (modifier) {
      Object.keys(modifier).forEach(function (key) {
        switch (key) {
          case 'name':
            if (typeof modifier.name !== 'string') {
              console.error(format(INVALID_MODIFIER_ERROR, String(modifier.name), '"name"', '"string"', "\"" + String(modifier.name) + "\""));
            }

            break;

          case 'enabled':
            if (typeof modifier.enabled !== 'boolean') {
              console.error(format(INVALID_MODIFIER_ERROR, modifier.name, '"enabled"', '"boolean"', "\"" + String(modifier.enabled) + "\""));
            }

          case 'phase':
            if (modifierPhases.indexOf(modifier.phase) < 0) {
              console.error(format(INVALID_MODIFIER_ERROR, modifier.name, '"phase"', "either " + modifierPhases.join(', '), "\"" + String(modifier.phase) + "\""));
            }

            break;

          case 'fn':
            if (typeof modifier.fn !== 'function') {
              console.error(format(INVALID_MODIFIER_ERROR, modifier.name, '"fn"', '"function"', "\"" + String(modifier.fn) + "\""));
            }

            break;

          case 'effect':
            if (typeof modifier.effect !== 'function') {
              console.error(format(INVALID_MODIFIER_ERROR, modifier.name, '"effect"', '"function"', "\"" + String(modifier.fn) + "\""));
            }

            break;

          case 'requires':
            if (!Array.isArray(modifier.requires)) {
              console.error(format(INVALID_MODIFIER_ERROR, modifier.name, '"requires"', '"array"', "\"" + String(modifier.requires) + "\""));
            }

            break;

          case 'requiresIfExists':
            if (!Array.isArray(modifier.requiresIfExists)) {
              console.error(format(INVALID_MODIFIER_ERROR, modifier.name, '"requiresIfExists"', '"array"', "\"" + String(modifier.requiresIfExists) + "\""));
            }

            break;

          case 'options':
          case 'data':
            break;

          default:
            console.error("PopperJS: an invalid property has been provided to the \"" + modifier.name + "\" modifier, valid properties are " + VALID_PROPERTIES.map(function (s) {
              return "\"" + s + "\"";
            }).join(', ') + "; but \"" + key + "\" was provided.");
        }

        modifier.requires && modifier.requires.forEach(function (requirement) {
          if (modifiers.find(function (mod) {
            return mod.name === requirement;
          }) == null) {
            console.error(format(MISSING_DEPENDENCY_ERROR, String(modifier.name), requirement, requirement));
          }
        });
      });
    });
  }

  function uniqueBy(arr, fn) {
    var identifiers = new Set();
    return arr.filter(function (item) {
      var identifier = fn(item);

      if (!identifiers.has(identifier)) {
        identifiers.add(identifier);
        return true;
      }
    });
  }

  function getBasePlacement(placement) {
    return placement.split('-')[0];
  }

  function mergeByName(modifiers) {
    var merged = modifiers.reduce(function (merged, current) {
      var existing = merged[current.name];
      merged[current.name] = existing ? Object.assign({}, existing, current, {
        options: Object.assign({}, existing.options, current.options),
        data: Object.assign({}, existing.data, current.data)
      }) : current;
      return merged;
    }, {}); // IE11 does not support Object.values

    return Object.keys(merged).map(function (key) {
      return merged[key];
    });
  }

  function getViewportRect(element) {
    var win = getWindow(element);
    var html = getDocumentElement(element);
    var visualViewport = win.visualViewport;
    var width = html.clientWidth;
    var height = html.clientHeight;
    var x = 0;
    var y = 0; // NB: This isn't supported on iOS <= 12. If the keyboard is open, the popper
    // can be obscured underneath it.
    // Also, `html.clientHeight` adds the bottom bar height in Safari iOS, even
    // if it isn't open, so if this isn't available, the popper will be detected
    // to overflow the bottom of the screen too early.

    if (visualViewport) {
      width = visualViewport.width;
      height = visualViewport.height; // Uses Layout Viewport (like Chrome; Safari does not currently)
      // In Chrome, it returns a value very close to 0 (+/-) but contains rounding
      // errors due to floating point numbers, so we need to check precision.
      // Safari returns a number <= 0, usually < -1 when pinch-zoomed
      // Feature detection fails in mobile emulation mode in Chrome.
      // Math.abs(win.innerWidth / visualViewport.scale - visualViewport.width) <
      // 0.001
      // Fallback here: "Not Safari" userAgent

      if (!/^((?!chrome|android).)*safari/i.test(navigator.userAgent)) {
        x = visualViewport.offsetLeft;
        y = visualViewport.offsetTop;
      }
    }

    return {
      width: width,
      height: height,
      x: x + getWindowScrollBarX(element),
      y: y
    };
  }

  var max = Math.max;
  var min = Math.min;
  var round = Math.round;

  // of the `<html>` and `<body>` rect bounds if horizontally scrollable

  function getDocumentRect(element) {
    var _element$ownerDocumen;

    var html = getDocumentElement(element);
    var winScroll = getWindowScroll(element);
    var body = (_element$ownerDocumen = element.ownerDocument) == null ? void 0 : _element$ownerDocumen.body;
    var width = max(html.scrollWidth, html.clientWidth, body ? body.scrollWidth : 0, body ? body.clientWidth : 0);
    var height = max(html.scrollHeight, html.clientHeight, body ? body.scrollHeight : 0, body ? body.clientHeight : 0);
    var x = -winScroll.scrollLeft + getWindowScrollBarX(element);
    var y = -winScroll.scrollTop;

    if (getComputedStyle(body || html).direction === 'rtl') {
      x += max(html.clientWidth, body ? body.clientWidth : 0) - width;
    }

    return {
      width: width,
      height: height,
      x: x,
      y: y
    };
  }

  function contains(parent, child) {
    var rootNode = child.getRootNode && child.getRootNode(); // First, attempt with faster native method

    if (parent.contains(child)) {
      return true;
    } // then fallback to custom implementation with Shadow DOM support
    else if (rootNode && isShadowRoot(rootNode)) {
      var next = child;

      do {
        if (next && parent.isSameNode(next)) {
          return true;
        } // $FlowFixMe[prop-missing]: need a better way to handle this...


        next = next.parentNode || next.host;
      } while (next);
    } // Give up, the result is false


    return false;
  }

  function rectToClientRect(rect) {
    return Object.assign({}, rect, {
      left: rect.x,
      top: rect.y,
      right: rect.x + rect.width,
      bottom: rect.y + rect.height
    });
  }

  function getInnerBoundingClientRect(element) {
    var rect = getBoundingClientRect(element);
    rect.top = rect.top + element.clientTop;
    rect.left = rect.left + element.clientLeft;
    rect.bottom = rect.top + element.clientHeight;
    rect.right = rect.left + element.clientWidth;
    rect.width = element.clientWidth;
    rect.height = element.clientHeight;
    rect.x = rect.left;
    rect.y = rect.top;
    return rect;
  }

  function getClientRectFromMixedType(element, clippingParent) {
    return clippingParent === viewport ? rectToClientRect(getViewportRect(element)) : isHTMLElement(clippingParent) ? getInnerBoundingClientRect(clippingParent) : rectToClientRect(getDocumentRect(getDocumentElement(element)));
  } // A "clipping parent" is an overflowable container with the characteristic of
  // clipping (or hiding) overflowing elements with a position different from
  // `initial`


  function getClippingParents(element) {
    var clippingParents = listScrollParents(getParentNode(element));
    var canEscapeClipping = ['absolute', 'fixed'].indexOf(getComputedStyle(element).position) >= 0;
    var clipperElement = canEscapeClipping && isHTMLElement(element) ? getOffsetParent(element) : element;

    if (!isElement(clipperElement)) {
      return [];
    } // $FlowFixMe[incompatible-return]: https://github.com/facebook/flow/issues/1414


    return clippingParents.filter(function (clippingParent) {
      return isElement(clippingParent) && contains(clippingParent, clipperElement) && getNodeName(clippingParent) !== 'body';
    });
  } // Gets the maximum area that the element is visible in due to any number of
  // clipping parents


  function getClippingRect(element, boundary, rootBoundary) {
    var mainClippingParents = boundary === 'clippingParents' ? getClippingParents(element) : [].concat(boundary);
    var clippingParents = [].concat(mainClippingParents, [rootBoundary]);
    var firstClippingParent = clippingParents[0];
    var clippingRect = clippingParents.reduce(function (accRect, clippingParent) {
      var rect = getClientRectFromMixedType(element, clippingParent);
      accRect.top = max(rect.top, accRect.top);
      accRect.right = min(rect.right, accRect.right);
      accRect.bottom = min(rect.bottom, accRect.bottom);
      accRect.left = max(rect.left, accRect.left);
      return accRect;
    }, getClientRectFromMixedType(element, firstClippingParent));
    clippingRect.width = clippingRect.right - clippingRect.left;
    clippingRect.height = clippingRect.bottom - clippingRect.top;
    clippingRect.x = clippingRect.left;
    clippingRect.y = clippingRect.top;
    return clippingRect;
  }

  function getVariation(placement) {
    return placement.split('-')[1];
  }

  function getMainAxisFromPlacement(placement) {
    return ['top', 'bottom'].indexOf(placement) >= 0 ? 'x' : 'y';
  }

  function computeOffsets(_ref) {
    var reference = _ref.reference,
      element = _ref.element,
      placement = _ref.placement;
    var basePlacement = placement ? getBasePlacement(placement) : null;
    var variation = placement ? getVariation(placement) : null;
    var commonX = reference.x + reference.width / 2 - element.width / 2;
    var commonY = reference.y + reference.height / 2 - element.height / 2;
    var offsets;

    switch (basePlacement) {
      case top:
        offsets = {
          x: commonX,
          y: reference.y - element.height
        };
        break;

      case bottom:
        offsets = {
          x: commonX,
          y: reference.y + reference.height
        };
        break;

      case right:
        offsets = {
          x: reference.x + reference.width,
          y: commonY
        };
        break;

      case left:
        offsets = {
          x: reference.x - element.width,
          y: commonY
        };
        break;

      default:
        offsets = {
          x: reference.x,
          y: reference.y
        };
    }

    var mainAxis = basePlacement ? getMainAxisFromPlacement(basePlacement) : null;

    if (mainAxis != null) {
      var len = mainAxis === 'y' ? 'height' : 'width';

      switch (variation) {
        case start:
          offsets[mainAxis] = offsets[mainAxis] - (reference[len] / 2 - element[len] / 2);
          break;

        case end:
          offsets[mainAxis] = offsets[mainAxis] + (reference[len] / 2 - element[len] / 2);
          break;
      }
    }

    return offsets;
  }

  function getFreshSideObject() {
    return {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0
    };
  }

  function mergePaddingObject(paddingObject) {
    return Object.assign({}, getFreshSideObject(), paddingObject);
  }

  function expandToHashMap(value, keys) {
    return keys.reduce(function (hashMap, key) {
      hashMap[key] = value;
      return hashMap;
    }, {});
  }

  function detectOverflow(state, options) {
    if (options === void 0) {
      options = {};
    }

    var _options = options,
      _options$placement = _options.placement,
      placement = _options$placement === void 0 ? state.placement : _options$placement,
      _options$boundary = _options.boundary,
      boundary = _options$boundary === void 0 ? clippingParents : _options$boundary,
      _options$rootBoundary = _options.rootBoundary,
      rootBoundary = _options$rootBoundary === void 0 ? viewport : _options$rootBoundary,
      _options$elementConte = _options.elementContext,
      elementContext = _options$elementConte === void 0 ? popper : _options$elementConte,
      _options$altBoundary = _options.altBoundary,
      altBoundary = _options$altBoundary === void 0 ? false : _options$altBoundary,
      _options$padding = _options.padding,
      padding = _options$padding === void 0 ? 0 : _options$padding;
    var paddingObject = mergePaddingObject(typeof padding !== 'number' ? padding : expandToHashMap(padding, basePlacements));
    var altContext = elementContext === popper ? reference : popper;
    var referenceElement = state.elements.reference;
    var popperRect = state.rects.popper;
    var element = state.elements[altBoundary ? altContext : elementContext];
    var clippingClientRect = getClippingRect(isElement(element) ? element : element.contextElement || getDocumentElement(state.elements.popper), boundary, rootBoundary);
    var referenceClientRect = getBoundingClientRect(referenceElement);
    var popperOffsets = computeOffsets({
      reference: referenceClientRect,
      element: popperRect,
      strategy: 'absolute',
      placement: placement
    });
    var popperClientRect = rectToClientRect(Object.assign({}, popperRect, popperOffsets));
    var elementClientRect = elementContext === popper ? popperClientRect : referenceClientRect; // positive = overflowing the clipping rect
    // 0 or negative = within the clipping rect

    var overflowOffsets = {
      top: clippingClientRect.top - elementClientRect.top + paddingObject.top,
      bottom: elementClientRect.bottom - clippingClientRect.bottom + paddingObject.bottom,
      left: clippingClientRect.left - elementClientRect.left + paddingObject.left,
      right: elementClientRect.right - clippingClientRect.right + paddingObject.right
    };
    var offsetData = state.modifiersData.offset; // Offsets can be applied only to the popper element

    if (elementContext === popper && offsetData) {
      var offset = offsetData[placement];
      Object.keys(overflowOffsets).forEach(function (key) {
        var multiply = [right, bottom].indexOf(key) >= 0 ? 1 : -1;
        var axis = [top, bottom].indexOf(key) >= 0 ? 'y' : 'x';
        overflowOffsets[key] += offset[axis] * multiply;
      });
    }

    return overflowOffsets;
  }

  var INVALID_ELEMENT_ERROR = 'Popper: Invalid reference or popper argument provided. They must be either a DOM element or virtual element.';
  var INFINITE_LOOP_ERROR = 'Popper: An infinite loop in the modifiers cycle has been detected! The cycle has been interrupted to prevent a browser crash.';
  var DEFAULT_OPTIONS = {
    placement: 'bottom',
    modifiers: [],
    strategy: 'absolute'
  };

  function areValidElements() {
    for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
      args[_key] = arguments[_key];
    }

    return !args.some(function (element) {
      return !(element && typeof element.getBoundingClientRect === 'function');
    });
  }

  function popperGenerator(generatorOptions) {
    if (generatorOptions === void 0) {
      generatorOptions = {};
    }

    var _generatorOptions = generatorOptions,
      _generatorOptions$def = _generatorOptions.defaultModifiers,
      defaultModifiers = _generatorOptions$def === void 0 ? [] : _generatorOptions$def,
      _generatorOptions$def2 = _generatorOptions.defaultOptions,
      defaultOptions = _generatorOptions$def2 === void 0 ? DEFAULT_OPTIONS : _generatorOptions$def2;
    return function createPopper(reference, popper, options) {
      if (options === void 0) {
        options = defaultOptions;
      }

      var state = {
        placement: 'bottom',
        orderedModifiers: [],
        options: Object.assign({}, DEFAULT_OPTIONS, defaultOptions),
        modifiersData: {},
        elements: {
          reference: reference,
          popper: popper
        },
        attributes: {},
        styles: {}
      };
      var effectCleanupFns = [];
      var isDestroyed = false;
      var instance = {
        state: state,
        setOptions: function setOptions(options) {
          cleanupModifierEffects();
          state.options = Object.assign({}, defaultOptions, state.options, options);
          state.scrollParents = {
            reference: isElement(reference) ? listScrollParents(reference) : reference.contextElement ? listScrollParents(reference.contextElement) : [],
            popper: listScrollParents(popper)
          }; // Orders the modifiers based on their dependencies and `phase`
          // properties

          var orderedModifiers = orderModifiers(mergeByName([].concat(defaultModifiers, state.options.modifiers))); // Strip out disabled modifiers

          state.orderedModifiers = orderedModifiers.filter(function (m) {
            return m.enabled;
          }); // Validate the provided modifiers so that the consumer will get warned
          // if one of the modifiers is invalid for any reason

          {
            var modifiers = uniqueBy([].concat(orderedModifiers, state.options.modifiers), function (_ref) {
              var name = _ref.name;
              return name;
            });
            validateModifiers(modifiers);

            if (getBasePlacement(state.options.placement) === auto) {
              var flipModifier = state.orderedModifiers.find(function (_ref2) {
                var name = _ref2.name;
                return name === 'flip';
              });

              if (!flipModifier) {
                console.error(['Popper: "auto" placements require the "flip" modifier be', 'present and enabled to work.'].join(' '));
              }
            }

            var _getComputedStyle = getComputedStyle(popper),
              marginTop = _getComputedStyle.marginTop,
              marginRight = _getComputedStyle.marginRight,
              marginBottom = _getComputedStyle.marginBottom,
              marginLeft = _getComputedStyle.marginLeft; // We no longer take into account `margins` on the popper, and it can
            // cause bugs with positioning, so we'll warn the consumer


            if ([marginTop, marginRight, marginBottom, marginLeft].some(function (margin) {
              return parseFloat(margin);
            })) {
              console.warn(['Popper: CSS "margin" styles cannot be used to apply padding', 'between the popper and its reference element or boundary.', 'To replicate margin, use the `offset` modifier, as well as', 'the `padding` option in the `preventOverflow` and `flip`', 'modifiers.'].join(' '));
            }
          }

          runModifierEffects();
          return instance.update();
        },
        // Sync update – it will always be executed, even if not necessary. This
        // is useful for low frequency updates where sync behavior simplifies the
        // logic.
        // For high frequency updates (e.g. `resize` and `scroll` events), always
        // prefer the async Popper#update method
        forceUpdate: function forceUpdate() {
          if (isDestroyed) {
            return;
          }

          var _state$elements = state.elements,
            reference = _state$elements.reference,
            popper = _state$elements.popper; // Don't proceed if `reference` or `popper` are not valid elements
          // anymore

          if (!areValidElements(reference, popper)) {
            {
              console.error(INVALID_ELEMENT_ERROR);
            }

            return;
          } // Store the reference and popper rects to be read by modifiers


          state.rects = {
            reference: getCompositeRect(reference, getOffsetParent(popper), state.options.strategy === 'fixed'),
            popper: getLayoutRect(popper)
          }; // Modifiers have the ability to reset the current update cycle. The
          // most common use case for this is the `flip` modifier changing the
          // placement, which then needs to re-run all the modifiers, because the
          // logic was previously ran for the previous placement and is therefore
          // stale/incorrect

          state.reset = false;
          state.placement = state.options.placement; // On each update cycle, the `modifiersData` property for each modifier
          // is filled with the initial data specified by the modifier. This means
          // it doesn't persist and is fresh on each update.
          // To ensure persistent data, use `${name}#persistent`

          state.orderedModifiers.forEach(function (modifier) {
            return state.modifiersData[modifier.name] = Object.assign({}, modifier.data);
          });
          var __debug_loops__ = 0;

          for (var index = 0; index < state.orderedModifiers.length; index++) {
            {
              __debug_loops__ += 1;

              if (__debug_loops__ > 100) {
                console.error(INFINITE_LOOP_ERROR);
                break;
              }
            }

            if (state.reset === true) {
              state.reset = false;
              index = -1;
              continue;
            }

            var _state$orderedModifie = state.orderedModifiers[index],
              fn = _state$orderedModifie.fn,
              _state$orderedModifie2 = _state$orderedModifie.options,
              _options = _state$orderedModifie2 === void 0 ? {} : _state$orderedModifie2,
              name = _state$orderedModifie.name;

            if (typeof fn === 'function') {
              state = fn({
                state: state,
                options: _options,
                name: name,
                instance: instance
              }) || state;
            }
          }
        },
        // Async and optimistically optimized update – it will not be executed if
        // not necessary (debounced to run at most once-per-tick)
        update: debounce(function () {
          return new Promise(function (resolve) {
            instance.forceUpdate();
            resolve(state);
          });
        }),
        destroy: function destroy() {
          cleanupModifierEffects();
          isDestroyed = true;
        }
      };

      if (!areValidElements(reference, popper)) {
        {
          console.error(INVALID_ELEMENT_ERROR);
        }

        return instance;
      }

      instance.setOptions(options).then(function (state) {
        if (!isDestroyed && options.onFirstUpdate) {
          options.onFirstUpdate(state);
        }
      }); // Modifiers have the ability to execute arbitrary code before the first
      // update cycle runs. They will be executed in the same order as the update
      // cycle. This is useful when a modifier adds some persistent data that
      // other modifiers need to use, but the modifier is run after the dependent
      // one.

      function runModifierEffects() {
        state.orderedModifiers.forEach(function (_ref3) {
          var name = _ref3.name,
            _ref3$options = _ref3.options,
            options = _ref3$options === void 0 ? {} : _ref3$options,
            effect = _ref3.effect;

          if (typeof effect === 'function') {
            var cleanupFn = effect({
              state: state,
              name: name,
              instance: instance,
              options: options
            });

            var noopFn = function noopFn() { };

            effectCleanupFns.push(cleanupFn || noopFn);
          }
        });
      }

      function cleanupModifierEffects() {
        effectCleanupFns.forEach(function (fn) {
          return fn();
        });
        effectCleanupFns = [];
      }

      return instance;
    };
  }

  var passive = {
    passive: true
  };

  function effect(_ref) {
    var state = _ref.state,
      instance = _ref.instance,
      options = _ref.options;
    var _options$scroll = options.scroll,
      scroll = _options$scroll === void 0 ? true : _options$scroll,
      _options$resize = options.resize,
      resize = _options$resize === void 0 ? true : _options$resize;
    var window = getWindow(state.elements.popper);
    var scrollParents = [].concat(state.scrollParents.reference, state.scrollParents.popper);

    if (scroll) {
      scrollParents.forEach(function (scrollParent) {
        scrollParent.addEventListener('scroll', instance.update, passive);
      });
    }

    if (resize) {
      window.addEventListener('resize', instance.update, passive);
    }

    return function () {
      if (scroll) {
        scrollParents.forEach(function (scrollParent) {
          scrollParent.removeEventListener('scroll', instance.update, passive);
        });
      }

      if (resize) {
        window.removeEventListener('resize', instance.update, passive);
      }
    };
  } // eslint-disable-next-line import/no-unused-modules


  var eventListeners = {
    name: 'eventListeners',
    enabled: true,
    phase: 'write',
    fn: function fn() { },
    effect: effect,
    data: {}
  };

  function popperOffsets(_ref) {
    var state = _ref.state,
      name = _ref.name;
    // Offsets are the actual position the popper needs to have to be
    // properly positioned near its reference element
    // This is the most basic placement, and will be adjusted by
    // the modifiers in the next step
    state.modifiersData[name] = computeOffsets({
      reference: state.rects.reference,
      element: state.rects.popper,
      strategy: 'absolute',
      placement: state.placement
    });
  } // eslint-disable-next-line import/no-unused-modules


  var popperOffsets$1 = {
    name: 'popperOffsets',
    enabled: true,
    phase: 'read',
    fn: popperOffsets,
    data: {}
  };

  var unsetSides = {
    top: 'auto',
    right: 'auto',
    bottom: 'auto',
    left: 'auto'
  }; // Round the offsets to the nearest suitable subpixel based on the DPR.
  // Zooming can change the DPR, but it seems to report a value that will
  // cleanly divide the values into the appropriate subpixels.

  function roundOffsetsByDPR(_ref) {
    var x = _ref.x,
      y = _ref.y;
    var win = window;
    var dpr = win.devicePixelRatio || 1;
    return {
      x: round(round(x * dpr) / dpr) || 0,
      y: round(round(y * dpr) / dpr) || 0
    };
  }

  function mapToStyles(_ref2) {
    var _Object$assign2;

    var popper = _ref2.popper,
      popperRect = _ref2.popperRect,
      placement = _ref2.placement,
      offsets = _ref2.offsets,
      position = _ref2.position,
      gpuAcceleration = _ref2.gpuAcceleration,
      adaptive = _ref2.adaptive,
      roundOffsets = _ref2.roundOffsets;

    var _ref3 = roundOffsets === true ? roundOffsetsByDPR(offsets) : typeof roundOffsets === 'function' ? roundOffsets(offsets) : offsets,
      _ref3$x = _ref3.x,
      x = _ref3$x === void 0 ? 0 : _ref3$x,
      _ref3$y = _ref3.y,
      y = _ref3$y === void 0 ? 0 : _ref3$y;

    var hasX = offsets.hasOwnProperty('x');
    var hasY = offsets.hasOwnProperty('y');
    var sideX = left;
    var sideY = top;
    var win = window;

    if (adaptive) {
      var offsetParent = getOffsetParent(popper);
      var heightProp = 'clientHeight';
      var widthProp = 'clientWidth';

      if (offsetParent === getWindow(popper)) {
        offsetParent = getDocumentElement(popper);

        if (getComputedStyle(offsetParent).position !== 'static') {
          heightProp = 'scrollHeight';
          widthProp = 'scrollWidth';
        }
      } // $FlowFixMe[incompatible-cast]: force type refinement, we compare offsetParent with window above, but Flow doesn't detect it

      /*:: offsetParent = (offsetParent: Element); */


      if (placement === top) {
        sideY = bottom; // $FlowFixMe[prop-missing]

        y -= offsetParent[heightProp] - popperRect.height;
        y *= gpuAcceleration ? 1 : -1;
      }

      if (placement === left) {
        sideX = right; // $FlowFixMe[prop-missing]

        x -= offsetParent[widthProp] - popperRect.width;
        x *= gpuAcceleration ? 1 : -1;
      }
    }

    var commonStyles = Object.assign({
      position: position
    }, adaptive && unsetSides);

    if (gpuAcceleration) {
      var _Object$assign;

      return Object.assign({}, commonStyles, (_Object$assign = {}, _Object$assign[sideY] = hasY ? '0' : '', _Object$assign[sideX] = hasX ? '0' : '', _Object$assign.transform = (win.devicePixelRatio || 1) < 2 ? "translate(" + x + "px, " + y + "px)" : "translate3d(" + x + "px, " + y + "px, 0)", _Object$assign));
    }

    return Object.assign({}, commonStyles, (_Object$assign2 = {}, _Object$assign2[sideY] = hasY ? y + "px" : '', _Object$assign2[sideX] = hasX ? x + "px" : '', _Object$assign2.transform = '', _Object$assign2));
  }

  function computeStyles(_ref4) {
    var state = _ref4.state,
      options = _ref4.options;
    var _options$gpuAccelerat = options.gpuAcceleration,
      gpuAcceleration = _options$gpuAccelerat === void 0 ? true : _options$gpuAccelerat,
      _options$adaptive = options.adaptive,
      adaptive = _options$adaptive === void 0 ? true : _options$adaptive,
      _options$roundOffsets = options.roundOffsets,
      roundOffsets = _options$roundOffsets === void 0 ? true : _options$roundOffsets;

    {
      var transitionProperty = getComputedStyle(state.elements.popper).transitionProperty || '';

      if (adaptive && ['transform', 'top', 'right', 'bottom', 'left'].some(function (property) {
        return transitionProperty.indexOf(property) >= 0;
      })) {
        console.warn(['Popper: Detected CSS transitions on at least one of the following', 'CSS properties: "transform", "top", "right", "bottom", "left".', '\n\n', 'Disable the "computeStyles" modifier\'s `adaptive` option to allow', 'for smooth transitions, or remove these properties from the CSS', 'transition declaration on the popper element if only transitioning', 'opacity or background-color for example.', '\n\n', 'We recommend using the popper element as a wrapper around an inner', 'element that can have any CSS property transitioned for animations.'].join(' '));
      }
    }

    var commonStyles = {
      placement: getBasePlacement(state.placement),
      popper: state.elements.popper,
      popperRect: state.rects.popper,
      gpuAcceleration: gpuAcceleration
    };

    if (state.modifiersData.popperOffsets != null) {
      state.styles.popper = Object.assign({}, state.styles.popper, mapToStyles(Object.assign({}, commonStyles, {
        offsets: state.modifiersData.popperOffsets,
        position: state.options.strategy,
        adaptive: adaptive,
        roundOffsets: roundOffsets
      })));
    }

    if (state.modifiersData.arrow != null) {
      state.styles.arrow = Object.assign({}, state.styles.arrow, mapToStyles(Object.assign({}, commonStyles, {
        offsets: state.modifiersData.arrow,
        position: 'absolute',
        adaptive: false,
        roundOffsets: roundOffsets
      })));
    }

    state.attributes.popper = Object.assign({}, state.attributes.popper, {
      'data-popper-placement': state.placement
    });
  } // eslint-disable-next-line import/no-unused-modules


  var computeStyles$1 = {
    name: 'computeStyles',
    enabled: true,
    phase: 'beforeWrite',
    fn: computeStyles,
    data: {}
  };

  // and applies them to the HTMLElements such as popper and arrow

  function applyStyles(_ref) {
    var state = _ref.state;
    Object.keys(state.elements).forEach(function (name) {
      var style = state.styles[name] || {};
      var attributes = state.attributes[name] || {};
      var element = state.elements[name]; // arrow is optional + virtual elements

      if (!isHTMLElement(element) || !getNodeName(element)) {
        return;
      } // Flow doesn't support to extend this property, but it's the most
      // effective way to apply styles to an HTMLElement
      // $FlowFixMe[cannot-write]


      Object.assign(element.style, style);
      Object.keys(attributes).forEach(function (name) {
        var value = attributes[name];

        if (value === false) {
          element.removeAttribute(name);
        } else {
          element.setAttribute(name, value === true ? '' : value);
        }
      });
    });
  }

  function effect$1(_ref2) {
    var state = _ref2.state;
    var initialStyles = {
      popper: {
        position: state.options.strategy,
        left: '0',
        top: '0',
        margin: '0'
      },
      arrow: {
        position: 'absolute'
      },
      reference: {}
    };
    Object.assign(state.elements.popper.style, initialStyles.popper);
    state.styles = initialStyles;

    if (state.elements.arrow) {
      Object.assign(state.elements.arrow.style, initialStyles.arrow);
    }

    return function () {
      Object.keys(state.elements).forEach(function (name) {
        var element = state.elements[name];
        var attributes = state.attributes[name] || {};
        var styleProperties = Object.keys(state.styles.hasOwnProperty(name) ? state.styles[name] : initialStyles[name]); // Set all values to an empty string to unset them

        var style = styleProperties.reduce(function (style, property) {
          style[property] = '';
          return style;
        }, {}); // arrow is optional + virtual elements

        if (!isHTMLElement(element) || !getNodeName(element)) {
          return;
        }

        Object.assign(element.style, style);
        Object.keys(attributes).forEach(function (attribute) {
          element.removeAttribute(attribute);
        });
      });
    };
  } // eslint-disable-next-line import/no-unused-modules


  var applyStyles$1 = {
    name: 'applyStyles',
    enabled: true,
    phase: 'write',
    fn: applyStyles,
    effect: effect$1,
    requires: ['computeStyles']
  };

  function distanceAndSkiddingToXY(placement, rects, offset) {
    var basePlacement = getBasePlacement(placement);
    var invertDistance = [left, top].indexOf(basePlacement) >= 0 ? -1 : 1;

    var _ref = typeof offset === 'function' ? offset(Object.assign({}, rects, {
      placement: placement
    })) : offset,
      skidding = _ref[0],
      distance = _ref[1];

    skidding = skidding || 0;
    distance = (distance || 0) * invertDistance;
    return [left, right].indexOf(basePlacement) >= 0 ? {
      x: distance,
      y: skidding
    } : {
        x: skidding,
        y: distance
      };
  }

  function offset(_ref2) {
    var state = _ref2.state,
      options = _ref2.options,
      name = _ref2.name;
    var _options$offset = options.offset,
      offset = _options$offset === void 0 ? [0, 0] : _options$offset;
    var data = placements.reduce(function (acc, placement) {
      acc[placement] = distanceAndSkiddingToXY(placement, state.rects, offset);
      return acc;
    }, {});
    var _data$state$placement = data[state.placement],
      x = _data$state$placement.x,
      y = _data$state$placement.y;

    if (state.modifiersData.popperOffsets != null) {
      state.modifiersData.popperOffsets.x += x;
      state.modifiersData.popperOffsets.y += y;
    }

    state.modifiersData[name] = data;
  } // eslint-disable-next-line import/no-unused-modules


  var offset$1 = {
    name: 'offset',
    enabled: true,
    phase: 'main',
    requires: ['popperOffsets'],
    fn: offset
  };

  var hash = {
    left: 'right',
    right: 'left',
    bottom: 'top',
    top: 'bottom'
  };
  function getOppositePlacement(placement) {
    return placement.replace(/left|right|bottom|top/g, function (matched) {
      return hash[matched];
    });
  }

  var hash$1 = {
    start: 'end',
    end: 'start'
  };
  function getOppositeVariationPlacement(placement) {
    return placement.replace(/start|end/g, function (matched) {
      return hash$1[matched];
    });
  }

  /*:: type OverflowsMap = { [ComputedPlacement]: number }; */

  /*;; type OverflowsMap = { [key in ComputedPlacement]: number }; */
  function computeAutoPlacement(state, options) {
    if (options === void 0) {
      options = {};
    }

    var _options = options,
      placement = _options.placement,
      boundary = _options.boundary,
      rootBoundary = _options.rootBoundary,
      padding = _options.padding,
      flipVariations = _options.flipVariations,
      _options$allowedAutoP = _options.allowedAutoPlacements,
      allowedAutoPlacements = _options$allowedAutoP === void 0 ? placements : _options$allowedAutoP;
    var variation = getVariation(placement);
    var placements$1 = variation ? flipVariations ? variationPlacements : variationPlacements.filter(function (placement) {
      return getVariation(placement) === variation;
    }) : basePlacements;
    var allowedPlacements = placements$1.filter(function (placement) {
      return allowedAutoPlacements.indexOf(placement) >= 0;
    });

    if (allowedPlacements.length === 0) {
      allowedPlacements = placements$1;

      {
        console.error(['Popper: The `allowedAutoPlacements` option did not allow any', 'placements. Ensure the `placement` option matches the variation', 'of the allowed placements.', 'For example, "auto" cannot be used to allow "bottom-start".', 'Use "auto-start" instead.'].join(' '));
      }
    } // $FlowFixMe[incompatible-type]: Flow seems to have problems with two array unions...


    var overflows = allowedPlacements.reduce(function (acc, placement) {
      acc[placement] = detectOverflow(state, {
        placement: placement,
        boundary: boundary,
        rootBoundary: rootBoundary,
        padding: padding
      })[getBasePlacement(placement)];
      return acc;
    }, {});
    return Object.keys(overflows).sort(function (a, b) {
      return overflows[a] - overflows[b];
    });
  }

  function getExpandedFallbackPlacements(placement) {
    if (getBasePlacement(placement) === auto) {
      return [];
    }

    var oppositePlacement = getOppositePlacement(placement);
    return [getOppositeVariationPlacement(placement), oppositePlacement, getOppositeVariationPlacement(oppositePlacement)];
  }

  function flip(_ref) {
    var state = _ref.state,
      options = _ref.options,
      name = _ref.name;

    if (state.modifiersData[name]._skip) {
      return;
    }

    var _options$mainAxis = options.mainAxis,
      checkMainAxis = _options$mainAxis === void 0 ? true : _options$mainAxis,
      _options$altAxis = options.altAxis,
      checkAltAxis = _options$altAxis === void 0 ? true : _options$altAxis,
      specifiedFallbackPlacements = options.fallbackPlacements,
      padding = options.padding,
      boundary = options.boundary,
      rootBoundary = options.rootBoundary,
      altBoundary = options.altBoundary,
      _options$flipVariatio = options.flipVariations,
      flipVariations = _options$flipVariatio === void 0 ? true : _options$flipVariatio,
      allowedAutoPlacements = options.allowedAutoPlacements;
    var preferredPlacement = state.options.placement;
    var basePlacement = getBasePlacement(preferredPlacement);
    var isBasePlacement = basePlacement === preferredPlacement;
    var fallbackPlacements = specifiedFallbackPlacements || (isBasePlacement || !flipVariations ? [getOppositePlacement(preferredPlacement)] : getExpandedFallbackPlacements(preferredPlacement));
    var placements = [preferredPlacement].concat(fallbackPlacements).reduce(function (acc, placement) {
      return acc.concat(getBasePlacement(placement) === auto ? computeAutoPlacement(state, {
        placement: placement,
        boundary: boundary,
        rootBoundary: rootBoundary,
        padding: padding,
        flipVariations: flipVariations,
        allowedAutoPlacements: allowedAutoPlacements
      }) : placement);
    }, []);
    var referenceRect = state.rects.reference;
    var popperRect = state.rects.popper;
    var checksMap = new Map();
    var makeFallbackChecks = true;
    var firstFittingPlacement = placements[0];

    for (var i = 0; i < placements.length; i++) {
      var placement = placements[i];

      var _basePlacement = getBasePlacement(placement);

      var isStartVariation = getVariation(placement) === start;
      var isVertical = [top, bottom].indexOf(_basePlacement) >= 0;
      var len = isVertical ? 'width' : 'height';
      var overflow = detectOverflow(state, {
        placement: placement,
        boundary: boundary,
        rootBoundary: rootBoundary,
        altBoundary: altBoundary,
        padding: padding
      });
      var mainVariationSide = isVertical ? isStartVariation ? right : left : isStartVariation ? bottom : top;

      if (referenceRect[len] > popperRect[len]) {
        mainVariationSide = getOppositePlacement(mainVariationSide);
      }

      var altVariationSide = getOppositePlacement(mainVariationSide);
      var checks = [];

      if (checkMainAxis) {
        checks.push(overflow[_basePlacement] <= 0);
      }

      if (checkAltAxis) {
        checks.push(overflow[mainVariationSide] <= 0, overflow[altVariationSide] <= 0);
      }

      if (checks.every(function (check) {
        return check;
      })) {
        firstFittingPlacement = placement;
        makeFallbackChecks = false;
        break;
      }

      checksMap.set(placement, checks);
    }

    if (makeFallbackChecks) {
      // `2` may be desired in some cases – research later
      var numberOfChecks = flipVariations ? 3 : 1;

      var _loop = function _loop(_i) {
        var fittingPlacement = placements.find(function (placement) {
          var checks = checksMap.get(placement);

          if (checks) {
            return checks.slice(0, _i).every(function (check) {
              return check;
            });
          }
        });

        if (fittingPlacement) {
          firstFittingPlacement = fittingPlacement;
          return "break";
        }
      };

      for (var _i = numberOfChecks; _i > 0; _i--) {
        var _ret = _loop(_i);

        if (_ret === "break") break;
      }
    }

    if (state.placement !== firstFittingPlacement) {
      state.modifiersData[name]._skip = true;
      state.placement = firstFittingPlacement;
      state.reset = true;
    }
  } // eslint-disable-next-line import/no-unused-modules


  var flip$1 = {
    name: 'flip',
    enabled: true,
    phase: 'main',
    fn: flip,
    requiresIfExists: ['offset'],
    data: {
      _skip: false
    }
  };

  function getAltAxis(axis) {
    return axis === 'x' ? 'y' : 'x';
  }

  function within(min$1, value, max$1) {
    return max(min$1, min(value, max$1));
  }

  function preventOverflow(_ref) {
    var state = _ref.state,
      options = _ref.options,
      name = _ref.name;
    var _options$mainAxis = options.mainAxis,
      checkMainAxis = _options$mainAxis === void 0 ? true : _options$mainAxis,
      _options$altAxis = options.altAxis,
      checkAltAxis = _options$altAxis === void 0 ? false : _options$altAxis,
      boundary = options.boundary,
      rootBoundary = options.rootBoundary,
      altBoundary = options.altBoundary,
      padding = options.padding,
      _options$tether = options.tether,
      tether = _options$tether === void 0 ? true : _options$tether,
      _options$tetherOffset = options.tetherOffset,
      tetherOffset = _options$tetherOffset === void 0 ? 0 : _options$tetherOffset;
    var overflow = detectOverflow(state, {
      boundary: boundary,
      rootBoundary: rootBoundary,
      padding: padding,
      altBoundary: altBoundary
    });
    var basePlacement = getBasePlacement(state.placement);
    var variation = getVariation(state.placement);
    var isBasePlacement = !variation;
    var mainAxis = getMainAxisFromPlacement(basePlacement);
    var altAxis = getAltAxis(mainAxis);
    var popperOffsets = state.modifiersData.popperOffsets;
    var referenceRect = state.rects.reference;
    var popperRect = state.rects.popper;
    var tetherOffsetValue = typeof tetherOffset === 'function' ? tetherOffset(Object.assign({}, state.rects, {
      placement: state.placement
    })) : tetherOffset;
    var data = {
      x: 0,
      y: 0
    };

    if (!popperOffsets) {
      return;
    }

    if (checkMainAxis || checkAltAxis) {
      var mainSide = mainAxis === 'y' ? top : left;
      var altSide = mainAxis === 'y' ? bottom : right;
      var len = mainAxis === 'y' ? 'height' : 'width';
      var offset = popperOffsets[mainAxis];
      var min$1 = popperOffsets[mainAxis] + overflow[mainSide];
      var max$1 = popperOffsets[mainAxis] - overflow[altSide];
      var additive = tether ? -popperRect[len] / 2 : 0;
      var minLen = variation === start ? referenceRect[len] : popperRect[len];
      var maxLen = variation === start ? -popperRect[len] : -referenceRect[len]; // We need to include the arrow in the calculation so the arrow doesn't go
      // outside the reference bounds

      var arrowElement = state.elements.arrow;
      var arrowRect = tether && arrowElement ? getLayoutRect(arrowElement) : {
        width: 0,
        height: 0
      };
      var arrowPaddingObject = state.modifiersData['arrow#persistent'] ? state.modifiersData['arrow#persistent'].padding : getFreshSideObject();
      var arrowPaddingMin = arrowPaddingObject[mainSide];
      var arrowPaddingMax = arrowPaddingObject[altSide]; // If the reference length is smaller than the arrow length, we don't want
      // to include its full size in the calculation. If the reference is small
      // and near the edge of a boundary, the popper can overflow even if the
      // reference is not overflowing as well (e.g. virtual elements with no
      // width or height)

      var arrowLen = within(0, referenceRect[len], arrowRect[len]);
      var minOffset = isBasePlacement ? referenceRect[len] / 2 - additive - arrowLen - arrowPaddingMin - tetherOffsetValue : minLen - arrowLen - arrowPaddingMin - tetherOffsetValue;
      var maxOffset = isBasePlacement ? -referenceRect[len] / 2 + additive + arrowLen + arrowPaddingMax + tetherOffsetValue : maxLen + arrowLen + arrowPaddingMax + tetherOffsetValue;
      var arrowOffsetParent = state.elements.arrow && getOffsetParent(state.elements.arrow);
      var clientOffset = arrowOffsetParent ? mainAxis === 'y' ? arrowOffsetParent.clientTop || 0 : arrowOffsetParent.clientLeft || 0 : 0;
      var offsetModifierValue = state.modifiersData.offset ? state.modifiersData.offset[state.placement][mainAxis] : 0;
      var tetherMin = popperOffsets[mainAxis] + minOffset - offsetModifierValue - clientOffset;
      var tetherMax = popperOffsets[mainAxis] + maxOffset - offsetModifierValue;

      if (checkMainAxis) {
        var preventedOffset = within(tether ? min(min$1, tetherMin) : min$1, offset, tether ? max(max$1, tetherMax) : max$1);
        popperOffsets[mainAxis] = preventedOffset;
        data[mainAxis] = preventedOffset - offset;
      }

      if (checkAltAxis) {
        var _mainSide = mainAxis === 'x' ? top : left;

        var _altSide = mainAxis === 'x' ? bottom : right;

        var _offset = popperOffsets[altAxis];

        var _min = _offset + overflow[_mainSide];

        var _max = _offset - overflow[_altSide];

        var _preventedOffset = within(tether ? min(_min, tetherMin) : _min, _offset, tether ? max(_max, tetherMax) : _max);

        popperOffsets[altAxis] = _preventedOffset;
        data[altAxis] = _preventedOffset - _offset;
      }
    }

    state.modifiersData[name] = data;
  } // eslint-disable-next-line import/no-unused-modules


  var preventOverflow$1 = {
    name: 'preventOverflow',
    enabled: true,
    phase: 'main',
    fn: preventOverflow,
    requiresIfExists: ['offset']
  };

  var toPaddingObject = function toPaddingObject(padding, state) {
    padding = typeof padding === 'function' ? padding(Object.assign({}, state.rects, {
      placement: state.placement
    })) : padding;
    return mergePaddingObject(typeof padding !== 'number' ? padding : expandToHashMap(padding, basePlacements));
  };

  function arrow(_ref) {
    var _state$modifiersData$;

    var state = _ref.state,
      name = _ref.name,
      options = _ref.options;
    var arrowElement = state.elements.arrow;
    var popperOffsets = state.modifiersData.popperOffsets;
    var basePlacement = getBasePlacement(state.placement);
    var axis = getMainAxisFromPlacement(basePlacement);
    var isVertical = [left, right].indexOf(basePlacement) >= 0;
    var len = isVertical ? 'height' : 'width';

    if (!arrowElement || !popperOffsets) {
      return;
    }

    var paddingObject = toPaddingObject(options.padding, state);
    var arrowRect = getLayoutRect(arrowElement);
    var minProp = axis === 'y' ? top : left;
    var maxProp = axis === 'y' ? bottom : right;
    var endDiff = state.rects.reference[len] + state.rects.reference[axis] - popperOffsets[axis] - state.rects.popper[len];
    var startDiff = popperOffsets[axis] - state.rects.reference[axis];
    var arrowOffsetParent = getOffsetParent(arrowElement);
    var clientSize = arrowOffsetParent ? axis === 'y' ? arrowOffsetParent.clientHeight || 0 : arrowOffsetParent.clientWidth || 0 : 0;
    var centerToReference = endDiff / 2 - startDiff / 2; // Make sure the arrow doesn't overflow the popper if the center point is
    // outside of the popper bounds

    var min = paddingObject[minProp];
    var max = clientSize - arrowRect[len] - paddingObject[maxProp];
    var center = clientSize / 2 - arrowRect[len] / 2 + centerToReference;
    var offset = within(min, center, max); // Prevents breaking syntax highlighting...

    var axisProp = axis;
    state.modifiersData[name] = (_state$modifiersData$ = {}, _state$modifiersData$[axisProp] = offset, _state$modifiersData$.centerOffset = offset - center, _state$modifiersData$);
  }

  function effect$2(_ref2) {
    var state = _ref2.state,
      options = _ref2.options;
    var _options$element = options.element,
      arrowElement = _options$element === void 0 ? '[data-popper-arrow]' : _options$element;

    if (arrowElement == null) {
      return;
    } // CSS selector


    if (typeof arrowElement === 'string') {
      arrowElement = state.elements.popper.querySelector(arrowElement);

      if (!arrowElement) {
        return;
      }
    }

    {
      if (!isHTMLElement(arrowElement)) {
        console.error(['Popper: "arrow" element must be an HTMLElement (not an SVGElement).', 'To use an SVG arrow, wrap it in an HTMLElement that will be used as', 'the arrow.'].join(' '));
      }
    }

    if (!contains(state.elements.popper, arrowElement)) {
      {
        console.error(['Popper: "arrow" modifier\'s `element` must be a child of the popper', 'element.'].join(' '));
      }

      return;
    }

    state.elements.arrow = arrowElement;
  } // eslint-disable-next-line import/no-unused-modules


  var arrow$1 = {
    name: 'arrow',
    enabled: true,
    phase: 'main',
    fn: arrow,
    effect: effect$2,
    requires: ['popperOffsets'],
    requiresIfExists: ['preventOverflow']
  };

  function getSideOffsets(overflow, rect, preventedOffsets) {
    if (preventedOffsets === void 0) {
      preventedOffsets = {
        x: 0,
        y: 0
      };
    }

    return {
      top: overflow.top - rect.height - preventedOffsets.y,
      right: overflow.right - rect.width + preventedOffsets.x,
      bottom: overflow.bottom - rect.height + preventedOffsets.y,
      left: overflow.left - rect.width - preventedOffsets.x
    };
  }

  function isAnySideFullyClipped(overflow) {
    return [top, right, bottom, left].some(function (side) {
      return overflow[side] >= 0;
    });
  }

  function hide(_ref) {
    var state = _ref.state,
      name = _ref.name;
    var referenceRect = state.rects.reference;
    var popperRect = state.rects.popper;
    var preventedOffsets = state.modifiersData.preventOverflow;
    var referenceOverflow = detectOverflow(state, {
      elementContext: 'reference'
    });
    var popperAltOverflow = detectOverflow(state, {
      altBoundary: true
    });
    var referenceClippingOffsets = getSideOffsets(referenceOverflow, referenceRect);
    var popperEscapeOffsets = getSideOffsets(popperAltOverflow, popperRect, preventedOffsets);
    var isReferenceHidden = isAnySideFullyClipped(referenceClippingOffsets);
    var hasPopperEscaped = isAnySideFullyClipped(popperEscapeOffsets);
    state.modifiersData[name] = {
      referenceClippingOffsets: referenceClippingOffsets,
      popperEscapeOffsets: popperEscapeOffsets,
      isReferenceHidden: isReferenceHidden,
      hasPopperEscaped: hasPopperEscaped
    };
    state.attributes.popper = Object.assign({}, state.attributes.popper, {
      'data-popper-reference-hidden': isReferenceHidden,
      'data-popper-escaped': hasPopperEscaped
    });
  } // eslint-disable-next-line import/no-unused-modules


  var hide$1 = {
    name: 'hide',
    enabled: true,
    phase: 'main',
    requiresIfExists: ['preventOverflow'],
    fn: hide
  };

  var defaultModifiers = [eventListeners, popperOffsets$1, computeStyles$1, applyStyles$1];
  var createPopper = /*#__PURE__*/popperGenerator({
    defaultModifiers: defaultModifiers
  }); // eslint-disable-next-line import/no-unused-modules

  var defaultModifiers$1 = [eventListeners, popperOffsets$1, computeStyles$1, applyStyles$1, offset$1, flip$1, preventOverflow$1, arrow$1, hide$1];
  var createPopper$1 = /*#__PURE__*/popperGenerator({
    defaultModifiers: defaultModifiers$1
  }); // eslint-disable-next-line import/no-unused-modules

  exports.applyStyles = applyStyles$1;
  exports.arrow = arrow$1;
  exports.computeStyles = computeStyles$1;
  exports.createPopper = createPopper$1;
  exports.createPopperLite = createPopper;
  exports.defaultModifiers = defaultModifiers$1;
  exports.detectOverflow = detectOverflow;
  exports.eventListeners = eventListeners;
  exports.flip = flip$1;
  exports.hide = hide$1;
  exports.offset = offset$1;
  exports.popperGenerator = popperGenerator;
  exports.popperOffsets = popperOffsets$1;
  exports.preventOverflow = preventOverflow$1;

  Object.defineProperty(exports, '__esModule', { value: true });

})));
//# sourceMappingURL=popper.js.map

/*!
  * Bootstrap v4.1.3 (https://getbootstrap.com/)
  * Copyright 2011-2018 The Bootstrap Authors (https://github.com/twbs/bootstrap/graphs/contributors)
  * Licensed under MIT (https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
!function (t, e) { "object" == typeof exports && "undefined" != typeof module ? e(exports, require("jquery"), require("popper.js")) : "function" == typeof define && define.amd ? define(["exports", "jquery", "popper.js"], e) : e(t.bootstrap = {}, t.jQuery, t.Popper) }(this, function (t, e, h) { "use strict"; function i(t, e) { for (var n = 0; n < e.length; n++) { var i = e[n]; i.enumerable = i.enumerable || !1, i.configurable = !0, "value" in i && (i.writable = !0), Object.defineProperty(t, i.key, i) } } function s(t, e, n) { return e && i(t.prototype, e), n && i(t, n), t } function l(r) { for (var t = 1; t < arguments.length; t++) { var o = null != arguments[t] ? arguments[t] : {}, e = Object.keys(o); "function" == typeof Object.getOwnPropertySymbols && (e = e.concat(Object.getOwnPropertySymbols(o).filter(function (t) { return Object.getOwnPropertyDescriptor(o, t).enumerable }))), e.forEach(function (t) { var e, n, i; e = r, i = o[n = t], n in e ? Object.defineProperty(e, n, { value: i, enumerable: !0, configurable: !0, writable: !0 }) : e[n] = i }) } return r } e = e && e.hasOwnProperty("default") ? e.default : e, h = h && h.hasOwnProperty("default") ? h.default : h; var r, n, o, a, c, u, f, d, g, _, m, p, v, y, E, C, T, b, S, I, A, D, w, N, O, k, P, j, H, L, R, x, W, U, q, F, K, M, Q, B, V, Y, z, J, Z, G, $, X, tt, et, nt, it, rt, ot, st, at, lt, ct, ht, ut, ft, dt, gt, _t, mt, pt, vt, yt, Et, Ct, Tt, bt, St, It, At, Dt, wt, Nt, Ot, kt, Pt, jt, Ht, Lt, Rt, xt, Wt, Ut, qt, Ft, Kt, Mt, Qt, Bt, Vt, Yt, zt, Jt, Zt, Gt, $t, Xt, te, ee, ne, ie, re, oe, se, ae, le, ce, he, ue, fe, de, ge, _e, me, pe, ve, ye, Ee, Ce, Te, be, Se, Ie, Ae, De, we, Ne, Oe, ke, Pe, je, He, Le, Re, xe, We, Ue, qe, Fe, Ke, Me, Qe, Be, Ve, Ye, ze, Je, Ze, Ge, $e, Xe, tn, en, nn, rn, on, sn, an, ln, cn, hn, un, fn, dn, gn, _n, mn, pn, vn, yn, En, Cn, Tn, bn, Sn, In, An, Dn, wn, Nn, On, kn, Pn, jn, Hn, Ln, Rn, xn, Wn, Un, qn, Fn = function (i) { var e = "transitionend"; function t(t) { var e = this, n = !1; return i(this).one(l.TRANSITION_END, function () { n = !0 }), setTimeout(function () { n || l.triggerTransitionEnd(e) }, t), this } var l = { TRANSITION_END: "bsTransitionEnd", getUID: function (t) { for (; t += ~~(1e6 * Math.random()), document.getElementById(t);); return t }, getSelectorFromElement: function (t) { var e = t.getAttribute("data-target"); e && "#" !== e || (e = t.getAttribute("href") || ""); try { return document.querySelector(e) ? e : null } catch (t) { return null } }, getTransitionDurationFromElement: function (t) { if (!t) return 0; var e = i(t).css("transition-duration"); return parseFloat(e) ? (e = e.split(",")[0], 1e3 * parseFloat(e)) : 0 }, reflow: function (t) { return t.offsetHeight }, triggerTransitionEnd: function (t) { i(t).trigger(e) }, supportsTransitionEnd: function () { return Boolean(e) }, isElement: function (t) { return (t[0] || t).nodeType }, typeCheckConfig: function (t, e, n) { for (var i in n) if (Object.prototype.hasOwnProperty.call(n, i)) { var r = n[i], o = e[i], s = o && l.isElement(o) ? "element" : (a = o, {}.toString.call(a).match(/\s([a-z]+)/i)[1].toLowerCase()); if (!new RegExp(r).test(s)) throw new Error(t.toUpperCase() + ': Option "' + i + '" provided type "' + s + '" but expected type "' + r + '".') } var a } }; return i.fn.emulateTransitionEnd = t, i.event.special[l.TRANSITION_END] = { bindType: e, delegateType: e, handle: function (t) { if (i(t.target).is(this)) return t.handleObj.handler.apply(this, arguments) } }, l }(e), Kn = (n = "alert", a = "." + (o = "bs.alert"), c = (r = e).fn[n], u = { CLOSE: "close" + a, CLOSED: "closed" + a, CLICK_DATA_API: "click" + a + ".data-api" }, f = "alert", d = "fade", g = "show", _ = function () { function i(t) { this._element = t } var t = i.prototype; return t.close = function (t) { var e = this._element; t && (e = this._getRootElement(t)), this._triggerCloseEvent(e).isDefaultPrevented() || this._removeElement(e) }, t.dispose = function () { r.removeData(this._element, o), this._element = null }, t._getRootElement = function (t) { var e = Fn.getSelectorFromElement(t), n = !1; return e && (n = document.querySelector(e)), n || (n = r(t).closest("." + f)[0]), n }, t._triggerCloseEvent = function (t) { var e = r.Event(u.CLOSE); return r(t).trigger(e), e }, t._removeElement = function (e) { var n = this; if (r(e).removeClass(g), r(e).hasClass(d)) { var t = Fn.getTransitionDurationFromElement(e); r(e).one(Fn.TRANSITION_END, function (t) { return n._destroyElement(e, t) }).emulateTransitionEnd(t) } else this._destroyElement(e) }, t._destroyElement = function (t) { r(t).detach().trigger(u.CLOSED).remove() }, i._jQueryInterface = function (n) { return this.each(function () { var t = r(this), e = t.data(o); e || (e = new i(this), t.data(o, e)), "close" === n && e[n](this) }) }, i._handleDismiss = function (e) { return function (t) { t && t.preventDefault(), e.close(this) } }, s(i, null, [{ key: "VERSION", get: function () { return "4.1.3" } }]), i }(), r(document).on(u.CLICK_DATA_API, '[data-dismiss="alert"]', _._handleDismiss(new _)), r.fn[n] = _._jQueryInterface, r.fn[n].Constructor = _, r.fn[n].noConflict = function () { return r.fn[n] = c, _._jQueryInterface }, _), Mn = (p = "button", y = "." + (v = "bs.button"), E = ".data-api", C = (m = e).fn[p], T = "active", b = "btn", I = '[data-toggle^="button"]', A = '[data-toggle="buttons"]', D = "input", w = ".active", N = ".btn", O = { CLICK_DATA_API: "click" + y + E, FOCUS_BLUR_DATA_API: (S = "focus") + y + E + " blur" + y + E }, k = function () { function n(t) { this._element = t } var t = n.prototype; return t.toggle = function () { var t = !0, e = !0, n = m(this._element).closest(A)[0]; if (n) { var i = this._element.querySelector(D); if (i) { if ("radio" === i.type) if (i.checked && this._element.classList.contains(T)) t = !1; else { var r = n.querySelector(w); r && m(r).removeClass(T) } if (t) { if (i.hasAttribute("disabled") || n.hasAttribute("disabled") || i.classList.contains("disabled") || n.classList.contains("disabled")) return; i.checked = !this._element.classList.contains(T), m(i).trigger("change") } i.focus(), e = !1 } } e && this._element.setAttribute("aria-pressed", !this._element.classList.contains(T)), t && m(this._element).toggleClass(T) }, t.dispose = function () { m.removeData(this._element, v), this._element = null }, n._jQueryInterface = function (e) { return this.each(function () { var t = m(this).data(v); t || (t = new n(this), m(this).data(v, t)), "toggle" === e && t[e]() }) }, s(n, null, [{ key: "VERSION", get: function () { return "4.1.3" } }]), n }(), m(document).on(O.CLICK_DATA_API, I, function (t) { t.preventDefault(); var e = t.target; m(e).hasClass(b) || (e = m(e).closest(N)), k._jQueryInterface.call(m(e), "toggle") }).on(O.FOCUS_BLUR_DATA_API, I, function (t) { var e = m(t.target).closest(N)[0]; m(e).toggleClass(S, /^focus(in)?$/.test(t.type)) }), m.fn[p] = k._jQueryInterface, m.fn[p].Constructor = k, m.fn[p].noConflict = function () { return m.fn[p] = C, k._jQueryInterface }, k), Qn = (j = "carousel", L = "." + (H = "bs.carousel"), R = ".data-api", x = (P = e).fn[j], W = { interval: 5e3, keyboard: !0, slide: !1, pause: "hover", wrap: !0 }, U = { interval: "(number|boolean)", keyboard: "boolean", slide: "(boolean|string)", pause: "(string|boolean)", wrap: "boolean" }, q = "next", F = "prev", K = "left", M = "right", Q = { SLIDE: "slide" + L, SLID: "slid" + L, KEYDOWN: "keydown" + L, MOUSEENTER: "mouseenter" + L, MOUSELEAVE: "mouseleave" + L, TOUCHEND: "touchend" + L, LOAD_DATA_API: "load" + L + R, CLICK_DATA_API: "click" + L + R }, B = "carousel", V = "active", Y = "slide", z = "carousel-item-right", J = "carousel-item-left", Z = "carousel-item-next", G = "carousel-item-prev", $ = ".active", X = ".active.carousel-item", tt = ".carousel-item", et = ".carousel-item-next, .carousel-item-prev", nt = ".carousel-indicators", it = "[data-slide], [data-slide-to]", rt = '[data-ride="carousel"]', ot = function () { function o(t, e) { this._items = null, this._interval = null, this._activeElement = null, this._isPaused = !1, this._isSliding = !1, this.touchTimeout = null, this._config = this._getConfig(e), this._element = P(t)[0], this._indicatorsElement = this._element.querySelector(nt), this._addEventListeners() } var t = o.prototype; return t.next = function () { this._isSliding || this._slide(q) }, t.nextWhenVisible = function () { !document.hidden && P(this._element).is(":visible") && "hidden" !== P(this._element).css("visibility") && this.next() }, t.prev = function () { this._isSliding || this._slide(F) }, t.pause = function (t) { t || (this._isPaused = !0), this._element.querySelector(et) && (Fn.triggerTransitionEnd(this._element), this.cycle(!0)), clearInterval(this._interval), this._interval = null }, t.cycle = function (t) { t || (this._isPaused = !1), this._interval && (clearInterval(this._interval), this._interval = null), this._config.interval && !this._isPaused && (this._interval = setInterval((document.visibilityState ? this.nextWhenVisible : this.next).bind(this), this._config.interval)) }, t.to = function (t) { var e = this; this._activeElement = this._element.querySelector(X); var n = this._getItemIndex(this._activeElement); if (!(t > this._items.length - 1 || t < 0)) if (this._isSliding) P(this._element).one(Q.SLID, function () { return e.to(t) }); else { if (n === t) return this.pause(), void this.cycle(); var i = n < t ? q : F; this._slide(i, this._items[t]) } }, t.dispose = function () { P(this._element).off(L), P.removeData(this._element, H), this._items = null, this._config = null, this._element = null, this._interval = null, this._isPaused = null, this._isSliding = null, this._activeElement = null, this._indicatorsElement = null }, t._getConfig = function (t) { return t = l({}, W, t), Fn.typeCheckConfig(j, t, U), t }, t._addEventListeners = function () { var e = this; this._config.keyboard && P(this._element).on(Q.KEYDOWN, function (t) { return e._keydown(t) }), "hover" === this._config.pause && (P(this._element).on(Q.MOUSEENTER, function (t) { return e.pause(t) }).on(Q.MOUSELEAVE, function (t) { return e.cycle(t) }), "ontouchstart" in document.documentElement && P(this._element).on(Q.TOUCHEND, function () { e.pause(), e.touchTimeout && clearTimeout(e.touchTimeout), e.touchTimeout = setTimeout(function (t) { return e.cycle(t) }, 500 + e._config.interval) })) }, t._keydown = function (t) { if (!/input|textarea/i.test(t.target.tagName)) switch (t.which) { case 37: t.preventDefault(), this.prev(); break; case 39: t.preventDefault(), this.next() } }, t._getItemIndex = function (t) { return this._items = t && t.parentNode ? [].slice.call(t.parentNode.querySelectorAll(tt)) : [], this._items.indexOf(t) }, t._getItemByDirection = function (t, e) { var n = t === q, i = t === F, r = this._getItemIndex(e), o = this._items.length - 1; if ((i && 0 === r || n && r === o) && !this._config.wrap) return e; var s = (r + (t === F ? -1 : 1)) % this._items.length; return -1 === s ? this._items[this._items.length - 1] : this._items[s] }, t._triggerSlideEvent = function (t, e) { var n = this._getItemIndex(t), i = this._getItemIndex(this._element.querySelector(X)), r = P.Event(Q.SLIDE, { relatedTarget: t, direction: e, from: i, to: n }); return P(this._element).trigger(r), r }, t._setActiveIndicatorElement = function (t) { if (this._indicatorsElement) { var e = [].slice.call(this._indicatorsElement.querySelectorAll($)); P(e).removeClass(V); var n = this._indicatorsElement.children[this._getItemIndex(t)]; n && P(n).addClass(V) } }, t._slide = function (t, e) { var n, i, r, o = this, s = this._element.querySelector(X), a = this._getItemIndex(s), l = e || s && this._getItemByDirection(t, s), c = this._getItemIndex(l), h = Boolean(this._interval); if (t === q ? (n = J, i = Z, r = K) : (n = z, i = G, r = M), l && P(l).hasClass(V)) this._isSliding = !1; else if (!this._triggerSlideEvent(l, r).isDefaultPrevented() && s && l) { this._isSliding = !0, h && this.pause(), this._setActiveIndicatorElement(l); var u = P.Event(Q.SLID, { relatedTarget: l, direction: r, from: a, to: c }); if (P(this._element).hasClass(Y)) { P(l).addClass(i), Fn.reflow(l), P(s).addClass(n), P(l).addClass(n); var f = Fn.getTransitionDurationFromElement(s); P(s).one(Fn.TRANSITION_END, function () { P(l).removeClass(n + " " + i).addClass(V), P(s).removeClass(V + " " + i + " " + n), o._isSliding = !1, setTimeout(function () { return P(o._element).trigger(u) }, 0) }).emulateTransitionEnd(f) } else P(s).removeClass(V), P(l).addClass(V), this._isSliding = !1, P(this._element).trigger(u); h && this.cycle() } }, o._jQueryInterface = function (i) { return this.each(function () { var t = P(this).data(H), e = l({}, W, P(this).data()); "object" == typeof i && (e = l({}, e, i)); var n = "string" == typeof i ? i : e.slide; if (t || (t = new o(this, e), P(this).data(H, t)), "number" == typeof i) t.to(i); else if ("string" == typeof n) { if ("undefined" == typeof t[n]) throw new TypeError('No method named "' + n + '"'); t[n]() } else e.interval && (t.pause(), t.cycle()) }) }, o._dataApiClickHandler = function (t) { var e = Fn.getSelectorFromElement(this); if (e) { var n = P(e)[0]; if (n && P(n).hasClass(B)) { var i = l({}, P(n).data(), P(this).data()), r = this.getAttribute("data-slide-to"); r && (i.interval = !1), o._jQueryInterface.call(P(n), i), r && P(n).data(H).to(r), t.preventDefault() } } }, s(o, null, [{ key: "VERSION", get: function () { return "4.1.3" } }, { key: "Default", get: function () { return W } }]), o }(), P(document).on(Q.CLICK_DATA_API, it, ot._dataApiClickHandler), P(window).on(Q.LOAD_DATA_API, function () { for (var t = [].slice.call(document.querySelectorAll(rt)), e = 0, n = t.length; e < n; e++) { var i = P(t[e]); ot._jQueryInterface.call(i, i.data()) } }), P.fn[j] = ot._jQueryInterface, P.fn[j].Constructor = ot, P.fn[j].noConflict = function () { return P.fn[j] = x, ot._jQueryInterface }, ot), Bn = (at = "collapse", ct = "." + (lt = "bs.collapse"), ht = (st = e).fn[at], ut = { toggle: !0, parent: "" }, ft = { toggle: "boolean", parent: "(string|element)" }, dt = { SHOW: "show" + ct, SHOWN: "shown" + ct, HIDE: "hide" + ct, HIDDEN: "hidden" + ct, CLICK_DATA_API: "click" + ct + ".data-api" }, gt = "show", _t = "collapse", mt = "collapsing", pt = "collapsed", vt = "width", yt = "height", Et = ".show, .collapsing", Ct = '[data-toggle="collapse"]', Tt = function () { function a(e, t) { this._isTransitioning = !1, this._element = e, this._config = this._getConfig(t), this._triggerArray = st.makeArray(document.querySelectorAll('[data-toggle="collapse"][href="#' + e.id + '"],[data-toggle="collapse"][data-target="#' + e.id + '"]')); for (var n = [].slice.call(document.querySelectorAll(Ct)), i = 0, r = n.length; i < r; i++) { var o = n[i], s = Fn.getSelectorFromElement(o), a = [].slice.call(document.querySelectorAll(s)).filter(function (t) { return t === e }); null !== s && 0 < a.length && (this._selector = s, this._triggerArray.push(o)) } this._parent = this._config.parent ? this._getParent() : null, this._config.parent || this._addAriaAndCollapsedClass(this._element, this._triggerArray), this._config.toggle && this.toggle() } var t = a.prototype; return t.toggle = function () { st(this._element).hasClass(gt) ? this.hide() : this.show() }, t.show = function () { var t, e, n = this; if (!this._isTransitioning && !st(this._element).hasClass(gt) && (this._parent && 0 === (t = [].slice.call(this._parent.querySelectorAll(Et)).filter(function (t) { return t.getAttribute("data-parent") === n._config.parent })).length && (t = null), !(t && (e = st(t).not(this._selector).data(lt)) && e._isTransitioning))) { var i = st.Event(dt.SHOW); if (st(this._element).trigger(i), !i.isDefaultPrevented()) { t && (a._jQueryInterface.call(st(t).not(this._selector), "hide"), e || st(t).data(lt, null)); var r = this._getDimension(); st(this._element).removeClass(_t).addClass(mt), this._element.style[r] = 0, this._triggerArray.length && st(this._triggerArray).removeClass(pt).attr("aria-expanded", !0), this.setTransitioning(!0); var o = "scroll" + (r[0].toUpperCase() + r.slice(1)), s = Fn.getTransitionDurationFromElement(this._element); st(this._element).one(Fn.TRANSITION_END, function () { st(n._element).removeClass(mt).addClass(_t).addClass(gt), n._element.style[r] = "", n.setTransitioning(!1), st(n._element).trigger(dt.SHOWN) }).emulateTransitionEnd(s), this._element.style[r] = this._element[o] + "px" } } }, t.hide = function () { var t = this; if (!this._isTransitioning && st(this._element).hasClass(gt)) { var e = st.Event(dt.HIDE); if (st(this._element).trigger(e), !e.isDefaultPrevented()) { var n = this._getDimension(); this._element.style[n] = this._element.getBoundingClientRect()[n] + "px", Fn.reflow(this._element), st(this._element).addClass(mt).removeClass(_t).removeClass(gt); var i = this._triggerArray.length; if (0 < i) for (var r = 0; r < i; r++) { var o = this._triggerArray[r], s = Fn.getSelectorFromElement(o); if (null !== s) st([].slice.call(document.querySelectorAll(s))).hasClass(gt) || st(o).addClass(pt).attr("aria-expanded", !1) } this.setTransitioning(!0); this._element.style[n] = ""; var a = Fn.getTransitionDurationFromElement(this._element); st(this._element).one(Fn.TRANSITION_END, function () { t.setTransitioning(!1), st(t._element).removeClass(mt).addClass(_t).trigger(dt.HIDDEN) }).emulateTransitionEnd(a) } } }, t.setTransitioning = function (t) { this._isTransitioning = t }, t.dispose = function () { st.removeData(this._element, lt), this._config = null, this._parent = null, this._element = null, this._triggerArray = null, this._isTransitioning = null }, t._getConfig = function (t) { return (t = l({}, ut, t)).toggle = Boolean(t.toggle), Fn.typeCheckConfig(at, t, ft), t }, t._getDimension = function () { return st(this._element).hasClass(vt) ? vt : yt }, t._getParent = function () { var n = this, t = null; Fn.isElement(this._config.parent) ? (t = this._config.parent, "undefined" != typeof this._config.parent.jquery && (t = this._config.parent[0])) : t = document.querySelector(this._config.parent); var e = '[data-toggle="collapse"][data-parent="' + this._config.parent + '"]', i = [].slice.call(t.querySelectorAll(e)); return st(i).each(function (t, e) { n._addAriaAndCollapsedClass(a._getTargetFromElement(e), [e]) }), t }, t._addAriaAndCollapsedClass = function (t, e) { if (t) { var n = st(t).hasClass(gt); e.length && st(e).toggleClass(pt, !n).attr("aria-expanded", n) } }, a._getTargetFromElement = function (t) { var e = Fn.getSelectorFromElement(t); return e ? document.querySelector(e) : null }, a._jQueryInterface = function (i) { return this.each(function () { var t = st(this), e = t.data(lt), n = l({}, ut, t.data(), "object" == typeof i && i ? i : {}); if (!e && n.toggle && /show|hide/.test(i) && (n.toggle = !1), e || (e = new a(this, n), t.data(lt, e)), "string" == typeof i) { if ("undefined" == typeof e[i]) throw new TypeError('No method named "' + i + '"'); e[i]() } }) }, s(a, null, [{ key: "VERSION", get: function () { return "4.1.3" } }, { key: "Default", get: function () { return ut } }]), a }(), st(document).on(dt.CLICK_DATA_API, Ct, function (t) { "A" === t.currentTarget.tagName && t.preventDefault(); var n = st(this), e = Fn.getSelectorFromElement(this), i = [].slice.call(document.querySelectorAll(e)); st(i).each(function () { var t = st(this), e = t.data(lt) ? "toggle" : n.data(); Tt._jQueryInterface.call(t, e) }) }), st.fn[at] = Tt._jQueryInterface, st.fn[at].Constructor = Tt, st.fn[at].noConflict = function () { return st.fn[at] = ht, Tt._jQueryInterface }, Tt), Vn = (St = "dropdown", At = "." + (It = "bs.dropdown"), Dt = ".data-api", wt = (bt = e).fn[St], Nt = new RegExp("38|40|27"), Ot = { HIDE: "hide" + At, HIDDEN: "hidden" + At, SHOW: "show" + At, SHOWN: "shown" + At, CLICK: "click" + At, CLICK_DATA_API: "click" + At + Dt, KEYDOWN_DATA_API: "keydown" + At + Dt, KEYUP_DATA_API: "keyup" + At + Dt }, kt = "disabled", Pt = "show", jt = "dropup", Ht = "dropright", Lt = "dropleft", Rt = "dropdown-menu-right", xt = "position-static", Wt = '[data-toggle="dropdown"]', Ut = ".dropdown form", qt = ".dropdown-menu", Ft = ".navbar-nav", Kt = ".dropdown-menu .dropdown-item:not(.disabled):not(:disabled)", Mt = "top-start", Qt = "top-end", Bt = "bottom-start", Vt = "bottom-end", Yt = "right-start", zt = "left-start", Jt = { offset: 0, flip: !0, boundary: "scrollParent", reference: "toggle", display: "dynamic" }, Zt = { offset: "(number|string|function)", flip: "boolean", boundary: "(string|element)", reference: "(string|element)", display: "string" }, Gt = function () { function c(t, e) { this._element = t, this._popper = null, this._config = this._getConfig(e), this._menu = this._getMenuElement(), this._inNavbar = this._detectNavbar(), this._addEventListeners() } var t = c.prototype; return t.toggle = function () { if (!this._element.disabled && !bt(this._element).hasClass(kt)) { var t = c._getParentFromElement(this._element), e = bt(this._menu).hasClass(Pt); if (c._clearMenus(), !e) { var n = { relatedTarget: this._element }, i = bt.Event(Ot.SHOW, n); if (bt(t).trigger(i), !i.isDefaultPrevented()) { if (!this._inNavbar) { if ("undefined" == typeof h) throw new TypeError("Bootstrap dropdown require Popper.js (https://popper.js.org)"); var r = this._element; "parent" === this._config.reference ? r = t : Fn.isElement(this._config.reference) && (r = this._config.reference, "undefined" != typeof this._config.reference.jquery && (r = this._config.reference[0])), "scrollParent" !== this._config.boundary && bt(t).addClass(xt), this._popper = new h(r, this._menu, this._getPopperConfig()) } "ontouchstart" in document.documentElement && 0 === bt(t).closest(Ft).length && bt(document.body).children().on("mouseover", null, bt.noop), this._element.focus(), this._element.setAttribute("aria-expanded", !0), bt(this._menu).toggleClass(Pt), bt(t).toggleClass(Pt).trigger(bt.Event(Ot.SHOWN, n)) } } } }, t.dispose = function () { bt.removeData(this._element, It), bt(this._element).off(At), this._element = null, (this._menu = null) !== this._popper && (this._popper.destroy(), this._popper = null) }, t.update = function () { this._inNavbar = this._detectNavbar(), null !== this._popper && this._popper.scheduleUpdate() }, t._addEventListeners = function () { var e = this; bt(this._element).on(Ot.CLICK, function (t) { t.preventDefault(), t.stopPropagation(), e.toggle() }) }, t._getConfig = function (t) { return t = l({}, this.constructor.Default, bt(this._element).data(), t), Fn.typeCheckConfig(St, t, this.constructor.DefaultType), t }, t._getMenuElement = function () { if (!this._menu) { var t = c._getParentFromElement(this._element); t && (this._menu = t.querySelector(qt)) } return this._menu }, t._getPlacement = function () { var t = bt(this._element.parentNode), e = Bt; return t.hasClass(jt) ? (e = Mt, bt(this._menu).hasClass(Rt) && (e = Qt)) : t.hasClass(Ht) ? e = Yt : t.hasClass(Lt) ? e = zt : bt(this._menu).hasClass(Rt) && (e = Vt), e }, t._detectNavbar = function () { return 0 < bt(this._element).closest(".navbar").length }, t._getPopperConfig = function () { var e = this, t = {}; "function" == typeof this._config.offset ? t.fn = function (t) { return t.offsets = l({}, t.offsets, e._config.offset(t.offsets) || {}), t } : t.offset = this._config.offset; var n = { placement: this._getPlacement(), modifiers: { offset: t, flip: { enabled: this._config.flip }, preventOverflow: { boundariesElement: this._config.boundary } } }; return "static" === this._config.display && (n.modifiers.applyStyle = { enabled: !1 }), n }, c._jQueryInterface = function (e) { return this.each(function () { var t = bt(this).data(It); if (t || (t = new c(this, "object" == typeof e ? e : null), bt(this).data(It, t)), "string" == typeof e) { if ("undefined" == typeof t[e]) throw new TypeError('No method named "' + e + '"'); t[e]() } }) }, c._clearMenus = function (t) { if (!t || 3 !== t.which && ("keyup" !== t.type || 9 === t.which)) for (var e = [].slice.call(document.querySelectorAll(Wt)), n = 0, i = e.length; n < i; n++) { var r = c._getParentFromElement(e[n]), o = bt(e[n]).data(It), s = { relatedTarget: e[n] }; if (t && "click" === t.type && (s.clickEvent = t), o) { var a = o._menu; if (bt(r).hasClass(Pt) && !(t && ("click" === t.type && /input|textarea/i.test(t.target.tagName) || "keyup" === t.type && 9 === t.which) && bt.contains(r, t.target))) { var l = bt.Event(Ot.HIDE, s); bt(r).trigger(l), l.isDefaultPrevented() || ("ontouchstart" in document.documentElement && bt(document.body).children().off("mouseover", null, bt.noop), e[n].setAttribute("aria-expanded", "false"), bt(a).removeClass(Pt), bt(r).removeClass(Pt).trigger(bt.Event(Ot.HIDDEN, s))) } } } }, c._getParentFromElement = function (t) { var e, n = Fn.getSelectorFromElement(t); return n && (e = document.querySelector(n)), e || t.parentNode }, c._dataApiKeydownHandler = function (t) { if ((/input|textarea/i.test(t.target.tagName) ? !(32 === t.which || 27 !== t.which && (40 !== t.which && 38 !== t.which || bt(t.target).closest(qt).length)) : Nt.test(t.which)) && (t.preventDefault(), t.stopPropagation(), !this.disabled && !bt(this).hasClass(kt))) { var e = c._getParentFromElement(this), n = bt(e).hasClass(Pt); if ((n || 27 === t.which && 32 === t.which) && (!n || 27 !== t.which && 32 !== t.which)) { var i = [].slice.call(e.querySelectorAll(Kt)); if (0 !== i.length) { var r = i.indexOf(t.target); 38 === t.which && 0 < r && r--, 40 === t.which && r < i.length - 1 && r++, r < 0 && (r = 0), i[r].focus() } } else { if (27 === t.which) { var o = e.querySelector(Wt); bt(o).trigger("focus") } bt(this).trigger("click") } } }, s(c, null, [{ key: "VERSION", get: function () { return "4.1.3" } }, { key: "Default", get: function () { return Jt } }, { key: "DefaultType", get: function () { return Zt } }]), c }(), bt(document).on(Ot.KEYDOWN_DATA_API, Wt, Gt._dataApiKeydownHandler).on(Ot.KEYDOWN_DATA_API, qt, Gt._dataApiKeydownHandler).on(Ot.CLICK_DATA_API + " " + Ot.KEYUP_DATA_API, Gt._clearMenus).on(Ot.CLICK_DATA_API, Wt, function (t) { t.preventDefault(), t.stopPropagation(), Gt._jQueryInterface.call(bt(this), "toggle") }).on(Ot.CLICK_DATA_API, Ut, function (t) { t.stopPropagation() }), bt.fn[St] = Gt._jQueryInterface, bt.fn[St].Constructor = Gt, bt.fn[St].noConflict = function () { return bt.fn[St] = wt, Gt._jQueryInterface }, Gt), Yn = (Xt = "modal", ee = "." + (te = "bs.modal"), ne = ($t = e).fn[Xt], ie = { backdrop: !0, keyboard: !0, focus: !0, show: !0 }, re = { backdrop: "(boolean|string)", keyboard: "boolean", focus: "boolean", show: "boolean" }, oe = { HIDE: "hide" + ee, HIDDEN: "hidden" + ee, SHOW: "show" + ee, SHOWN: "shown" + ee, FOCUSIN: "focusin" + ee, RESIZE: "resize" + ee, CLICK_DISMISS: "click.dismiss" + ee, KEYDOWN_DISMISS: "keydown.dismiss" + ee, MOUSEUP_DISMISS: "mouseup.dismiss" + ee, MOUSEDOWN_DISMISS: "mousedown.dismiss" + ee, CLICK_DATA_API: "click" + ee + ".data-api" }, se = "modal-scrollbar-measure", ae = "modal-backdrop", le = "modal-open", ce = "fade", he = "show", ue = ".modal-dialog", fe = '[data-toggle="modal"]', de = '[data-dismiss="modal"]', ge = ".fixed-top, .fixed-bottom, .is-fixed, .sticky-top", _e = ".sticky-top", me = function () { function r(t, e) { this._config = this._getConfig(e), this._element = t, this._dialog = t.querySelector(ue), this._backdrop = null, this._isShown = !1, this._isBodyOverflowing = !1, this._ignoreBackdropClick = !1, this._scrollbarWidth = 0 } var t = r.prototype; return t.toggle = function (t) { return this._isShown ? this.hide() : this.show(t) }, t.show = function (t) { var e = this; if (!this._isTransitioning && !this._isShown) { $t(this._element).hasClass(ce) && (this._isTransitioning = !0); var n = $t.Event(oe.SHOW, { relatedTarget: t }); $t(this._element).trigger(n), this._isShown || n.isDefaultPrevented() || (this._isShown = !0, this._checkScrollbar(), this._setScrollbar(), this._adjustDialog(), $t(document.body).addClass(le), this._setEscapeEvent(), this._setResizeEvent(), $t(this._element).on(oe.CLICK_DISMISS, de, function (t) { return e.hide(t) }), $t(this._dialog).on(oe.MOUSEDOWN_DISMISS, function () { $t(e._element).one(oe.MOUSEUP_DISMISS, function (t) { $t(t.target).is(e._element) && (e._ignoreBackdropClick = !0) }) }), this._showBackdrop(function () { return e._showElement(t) })) } }, t.hide = function (t) { var e = this; if (t && t.preventDefault(), !this._isTransitioning && this._isShown) { var n = $t.Event(oe.HIDE); if ($t(this._element).trigger(n), this._isShown && !n.isDefaultPrevented()) { this._isShown = !1; var i = $t(this._element).hasClass(ce); if (i && (this._isTransitioning = !0), this._setEscapeEvent(), this._setResizeEvent(), $t(document).off(oe.FOCUSIN), $t(this._element).removeClass(he), $t(this._element).off(oe.CLICK_DISMISS), $t(this._dialog).off(oe.MOUSEDOWN_DISMISS), i) { var r = Fn.getTransitionDurationFromElement(this._element); $t(this._element).one(Fn.TRANSITION_END, function (t) { return e._hideModal(t) }).emulateTransitionEnd(r) } else this._hideModal() } } }, t.dispose = function () { $t.removeData(this._element, te), $t(window, document, this._element, this._backdrop).off(ee), this._config = null, this._element = null, this._dialog = null, this._backdrop = null, this._isShown = null, this._isBodyOverflowing = null, this._ignoreBackdropClick = null, this._scrollbarWidth = null }, t.handleUpdate = function () { this._adjustDialog() }, t._getConfig = function (t) { return t = l({}, ie, t), Fn.typeCheckConfig(Xt, t, re), t }, t._showElement = function (t) { var e = this, n = $t(this._element).hasClass(ce); this._element.parentNode && this._element.parentNode.nodeType === Node.ELEMENT_NODE || document.body.appendChild(this._element), this._element.style.display = "block", this._element.removeAttribute("aria-hidden"), this._element.scrollTop = 0, n && Fn.reflow(this._element), $t(this._element).addClass(he), this._config.focus && this._enforceFocus(); var i = $t.Event(oe.SHOWN, { relatedTarget: t }), r = function () { e._config.focus && e._element.focus(), e._isTransitioning = !1, $t(e._element).trigger(i) }; if (n) { var o = Fn.getTransitionDurationFromElement(this._element); $t(this._dialog).one(Fn.TRANSITION_END, r).emulateTransitionEnd(o) } else r() }, t._enforceFocus = function () { var e = this; $t(document).off(oe.FOCUSIN).on(oe.FOCUSIN, function (t) { document !== t.target && e._element !== t.target && 0 === $t(e._element).has(t.target).length && e._element.focus() }) }, t._setEscapeEvent = function () { var e = this; this._isShown && this._config.keyboard ? $t(this._element).on(oe.KEYDOWN_DISMISS, function (t) { 27 === t.which && (t.preventDefault(), e.hide()) }) : this._isShown || $t(this._element).off(oe.KEYDOWN_DISMISS) }, t._setResizeEvent = function () { var e = this; this._isShown ? $t(window).on(oe.RESIZE, function (t) { return e.handleUpdate(t) }) : $t(window).off(oe.RESIZE) }, t._hideModal = function () { var t = this; this._element.style.display = "none", this._element.setAttribute("aria-hidden", !0), this._isTransitioning = !1, this._showBackdrop(function () { $t(document.body).removeClass(le), t._resetAdjustments(), t._resetScrollbar(), $t(t._element).trigger(oe.HIDDEN) }) }, t._removeBackdrop = function () { this._backdrop && ($t(this._backdrop).remove(), this._backdrop = null) }, t._showBackdrop = function (t) { var e = this, n = $t(this._element).hasClass(ce) ? ce : ""; if (this._isShown && this._config.backdrop) { if (this._backdrop = document.createElement("div"), this._backdrop.className = ae, n && this._backdrop.classList.add(n), $t(this._backdrop).appendTo(document.body), $t(this._element).on(oe.CLICK_DISMISS, function (t) { e._ignoreBackdropClick ? e._ignoreBackdropClick = !1 : t.target === t.currentTarget && ("static" === e._config.backdrop ? e._element.focus() : e.hide()) }), n && Fn.reflow(this._backdrop), $t(this._backdrop).addClass(he), !t) return; if (!n) return void t(); var i = Fn.getTransitionDurationFromElement(this._backdrop); $t(this._backdrop).one(Fn.TRANSITION_END, t).emulateTransitionEnd(i) } else if (!this._isShown && this._backdrop) { $t(this._backdrop).removeClass(he); var r = function () { e._removeBackdrop(), t && t() }; if ($t(this._element).hasClass(ce)) { var o = Fn.getTransitionDurationFromElement(this._backdrop); $t(this._backdrop).one(Fn.TRANSITION_END, r).emulateTransitionEnd(o) } else r() } else t && t() }, t._adjustDialog = function () { var t = this._element.scrollHeight > document.documentElement.clientHeight; !this._isBodyOverflowing && t && (this._element.style.paddingLeft = this._scrollbarWidth + "px"), this._isBodyOverflowing && !t && (this._element.style.paddingRight = this._scrollbarWidth + "px") }, t._resetAdjustments = function () { this._element.style.paddingLeft = "", this._element.style.paddingRight = "" }, t._checkScrollbar = function () { var t = document.body.getBoundingClientRect(); this._isBodyOverflowing = t.left + t.right < window.innerWidth, this._scrollbarWidth = this._getScrollbarWidth() }, t._setScrollbar = function () { var r = this; if (this._isBodyOverflowing) { var t = [].slice.call(document.querySelectorAll(ge)), e = [].slice.call(document.querySelectorAll(_e)); $t(t).each(function (t, e) { var n = e.style.paddingRight, i = $t(e).css("padding-right"); $t(e).data("padding-right", n).css("padding-right", parseFloat(i) + r._scrollbarWidth + "px") }), $t(e).each(function (t, e) { var n = e.style.marginRight, i = $t(e).css("margin-right"); $t(e).data("margin-right", n).css("margin-right", parseFloat(i) - r._scrollbarWidth + "px") }); var n = document.body.style.paddingRight, i = $t(document.body).css("padding-right"); $t(document.body).data("padding-right", n).css("padding-right", parseFloat(i) + this._scrollbarWidth + "px") } }, t._resetScrollbar = function () { var t = [].slice.call(document.querySelectorAll(ge)); $t(t).each(function (t, e) { var n = $t(e).data("padding-right"); $t(e).removeData("padding-right"), e.style.paddingRight = n || "" }); var e = [].slice.call(document.querySelectorAll("" + _e)); $t(e).each(function (t, e) { var n = $t(e).data("margin-right"); "undefined" != typeof n && $t(e).css("margin-right", n).removeData("margin-right") }); var n = $t(document.body).data("padding-right"); $t(document.body).removeData("padding-right"), document.body.style.paddingRight = n || "" }, t._getScrollbarWidth = function () { var t = document.createElement("div"); t.className = se, document.body.appendChild(t); var e = t.getBoundingClientRect().width - t.clientWidth; return document.body.removeChild(t), e }, r._jQueryInterface = function (n, i) { return this.each(function () { var t = $t(this).data(te), e = l({}, ie, $t(this).data(), "object" == typeof n && n ? n : {}); if (t || (t = new r(this, e), $t(this).data(te, t)), "string" == typeof n) { if ("undefined" == typeof t[n]) throw new TypeError('No method named "' + n + '"'); t[n](i) } else e.show && t.show(i) }) }, s(r, null, [{ key: "VERSION", get: function () { return "4.1.3" } }, { key: "Default", get: function () { return ie } }]), r }(), $t(document).on(oe.CLICK_DATA_API, fe, function (t) { var e, n = this, i = Fn.getSelectorFromElement(this); i && (e = document.querySelector(i)); var r = $t(e).data(te) ? "toggle" : l({}, $t(e).data(), $t(this).data()); "A" !== this.tagName && "AREA" !== this.tagName || t.preventDefault(); var o = $t(e).one(oe.SHOW, function (t) { t.isDefaultPrevented() || o.one(oe.HIDDEN, function () { $t(n).is(":visible") && n.focus() }) }); me._jQueryInterface.call($t(e), r, this) }), $t.fn[Xt] = me._jQueryInterface, $t.fn[Xt].Constructor = me, $t.fn[Xt].noConflict = function () { return $t.fn[Xt] = ne, me._jQueryInterface }, me), zn = (ve = "tooltip", Ee = "." + (ye = "bs.tooltip"), Ce = (pe = e).fn[ve], Te = "bs-tooltip", be = new RegExp("(^|\\s)" + Te + "\\S+", "g"), Ae = { animation: !0, template: '<div class="tooltip" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>', trigger: "hover focus", title: "", delay: 0, html: !(Ie = { AUTO: "auto", TOP: "top", RIGHT: "right", BOTTOM: "bottom", LEFT: "left" }), selector: !(Se = { animation: "boolean", template: "string", title: "(string|element|function)", trigger: "string", delay: "(number|object)", html: "boolean", selector: "(string|boolean)", placement: "(string|function)", offset: "(number|string)", container: "(string|element|boolean)", fallbackPlacement: "(string|array)", boundary: "(string|element)" }), placement: "top", offset: 0, container: !1, fallbackPlacement: "flip", boundary: "scrollParent" }, we = "out", Ne = { HIDE: "hide" + Ee, HIDDEN: "hidden" + Ee, SHOW: (De = "show") + Ee, SHOWN: "shown" + Ee, INSERTED: "inserted" + Ee, CLICK: "click" + Ee, FOCUSIN: "focusin" + Ee, FOCUSOUT: "focusout" + Ee, MOUSEENTER: "mouseenter" + Ee, MOUSELEAVE: "mouseleave" + Ee }, Oe = "fade", ke = "show", Pe = ".tooltip-inner", je = ".arrow", He = "hover", Le = "focus", Re = "click", xe = "manual", We = function () { function i(t, e) { if ("undefined" == typeof h) throw new TypeError("Bootstrap tooltips require Popper.js (https://popper.js.org)"); this._isEnabled = !0, this._timeout = 0, this._hoverState = "", this._activeTrigger = {}, this._popper = null, this.element = t, this.config = this._getConfig(e), this.tip = null, this._setListeners() } var t = i.prototype; return t.enable = function () { this._isEnabled = !0 }, t.disable = function () { this._isEnabled = !1 }, t.toggleEnabled = function () { this._isEnabled = !this._isEnabled }, t.toggle = function (t) { if (this._isEnabled) if (t) { var e = this.constructor.DATA_KEY, n = pe(t.currentTarget).data(e); n || (n = new this.constructor(t.currentTarget, this._getDelegateConfig()), pe(t.currentTarget).data(e, n)), n._activeTrigger.click = !n._activeTrigger.click, n._isWithActiveTrigger() ? n._enter(null, n) : n._leave(null, n) } else { if (pe(this.getTipElement()).hasClass(ke)) return void this._leave(null, this); this._enter(null, this) } }, t.dispose = function () { clearTimeout(this._timeout), pe.removeData(this.element, this.constructor.DATA_KEY), pe(this.element).off(this.constructor.EVENT_KEY), pe(this.element).closest(".modal").off("hide.bs.modal"), this.tip && pe(this.tip).remove(), this._isEnabled = null, this._timeout = null, this._hoverState = null, (this._activeTrigger = null) !== this._popper && this._popper.destroy(), this._popper = null, this.element = null, this.config = null, this.tip = null }, t.show = function () { var e = this; if ("none" === pe(this.element).css("display")) throw new Error("Please use show on visible elements"); var t = pe.Event(this.constructor.Event.SHOW); if (this.isWithContent() && this._isEnabled) { pe(this.element).trigger(t); var n = pe.contains(this.element.ownerDocument.documentElement, this.element); if (t.isDefaultPrevented() || !n) return; var i = this.getTipElement(), r = Fn.getUID(this.constructor.NAME); i.setAttribute("id", r), this.element.setAttribute("aria-describedby", r), this.setContent(), this.config.animation && pe(i).addClass(Oe); var o = "function" == typeof this.config.placement ? this.config.placement.call(this, i, this.element) : this.config.placement, s = this._getAttachment(o); this.addAttachmentClass(s); var a = !1 === this.config.container ? document.body : pe(document).find(this.config.container); pe(i).data(this.constructor.DATA_KEY, this), pe.contains(this.element.ownerDocument.documentElement, this.tip) || pe(i).appendTo(a), pe(this.element).trigger(this.constructor.Event.INSERTED), this._popper = new h(this.element, i, { placement: s, modifiers: { offset: { offset: this.config.offset }, flip: { behavior: this.config.fallbackPlacement }, arrow: { element: je }, preventOverflow: { boundariesElement: this.config.boundary } }, onCreate: function (t) { t.originalPlacement !== t.placement && e._handlePopperPlacementChange(t) }, onUpdate: function (t) { e._handlePopperPlacementChange(t) } }), pe(i).addClass(ke), "ontouchstart" in document.documentElement && pe(document.body).children().on("mouseover", null, pe.noop); var l = function () { e.config.animation && e._fixTransition(); var t = e._hoverState; e._hoverState = null, pe(e.element).trigger(e.constructor.Event.SHOWN), t === we && e._leave(null, e) }; if (pe(this.tip).hasClass(Oe)) { var c = Fn.getTransitionDurationFromElement(this.tip); pe(this.tip).one(Fn.TRANSITION_END, l).emulateTransitionEnd(c) } else l() } }, t.hide = function (t) { var e = this, n = this.getTipElement(), i = pe.Event(this.constructor.Event.HIDE), r = function () { e._hoverState !== De && n.parentNode && n.parentNode.removeChild(n), e._cleanTipClass(), e.element.removeAttribute("aria-describedby"), pe(e.element).trigger(e.constructor.Event.HIDDEN), null !== e._popper && e._popper.destroy(), t && t() }; if (pe(this.element).trigger(i), !i.isDefaultPrevented()) { if (pe(n).removeClass(ke), "ontouchstart" in document.documentElement && pe(document.body).children().off("mouseover", null, pe.noop), this._activeTrigger[Re] = !1, this._activeTrigger[Le] = !1, this._activeTrigger[He] = !1, pe(this.tip).hasClass(Oe)) { var o = Fn.getTransitionDurationFromElement(n); pe(n).one(Fn.TRANSITION_END, r).emulateTransitionEnd(o) } else r(); this._hoverState = "" } }, t.update = function () { null !== this._popper && this._popper.scheduleUpdate() }, t.isWithContent = function () { return Boolean(this.getTitle()) }, t.addAttachmentClass = function (t) { pe(this.getTipElement()).addClass(Te + "-" + t) }, t.getTipElement = function () { return this.tip = this.tip || pe(this.config.template)[0], this.tip }, t.setContent = function () { var t = this.getTipElement(); this.setElementContent(pe(t.querySelectorAll(Pe)), this.getTitle()), pe(t).removeClass(Oe + " " + ke) }, t.setElementContent = function (t, e) { var n = this.config.html; "object" == typeof e && (e.nodeType || e.jquery) ? n ? pe(e).parent().is(t) || t.empty().append(e) : t.text(pe(e).text()) : t[n ? "html" : "text"](e) }, t.getTitle = function () { var t = this.element.getAttribute("data-original-title"); return t || (t = "function" == typeof this.config.title ? this.config.title.call(this.element) : this.config.title), t }, t._getAttachment = function (t) { return Ie[t.toUpperCase()] }, t._setListeners = function () { var i = this; this.config.trigger.split(" ").forEach(function (t) { if ("click" === t) pe(i.element).on(i.constructor.Event.CLICK, i.config.selector, function (t) { return i.toggle(t) }); else if (t !== xe) { var e = t === He ? i.constructor.Event.MOUSEENTER : i.constructor.Event.FOCUSIN, n = t === He ? i.constructor.Event.MOUSELEAVE : i.constructor.Event.FOCUSOUT; pe(i.element).on(e, i.config.selector, function (t) { return i._enter(t) }).on(n, i.config.selector, function (t) { return i._leave(t) }) } pe(i.element).closest(".modal").on("hide.bs.modal", function () { return i.hide() }) }), this.config.selector ? this.config = l({}, this.config, { trigger: "manual", selector: "" }) : this._fixTitle() }, t._fixTitle = function () { var t = typeof this.element.getAttribute("data-original-title"); (this.element.getAttribute("title") || "string" !== t) && (this.element.setAttribute("data-original-title", this.element.getAttribute("title") || ""), this.element.setAttribute("title", "")) }, t._enter = function (t, e) { var n = this.constructor.DATA_KEY; (e = e || pe(t.currentTarget).data(n)) || (e = new this.constructor(t.currentTarget, this._getDelegateConfig()), pe(t.currentTarget).data(n, e)), t && (e._activeTrigger["focusin" === t.type ? Le : He] = !0), pe(e.getTipElement()).hasClass(ke) || e._hoverState === De ? e._hoverState = De : (clearTimeout(e._timeout), e._hoverState = De, e.config.delay && e.config.delay.show ? e._timeout = setTimeout(function () { e._hoverState === De && e.show() }, e.config.delay.show) : e.show()) }, t._leave = function (t, e) { var n = this.constructor.DATA_KEY; (e = e || pe(t.currentTarget).data(n)) || (e = new this.constructor(t.currentTarget, this._getDelegateConfig()), pe(t.currentTarget).data(n, e)), t && (e._activeTrigger["focusout" === t.type ? Le : He] = !1), e._isWithActiveTrigger() || (clearTimeout(e._timeout), e._hoverState = we, e.config.delay && e.config.delay.hide ? e._timeout = setTimeout(function () { e._hoverState === we && e.hide() }, e.config.delay.hide) : e.hide()) }, t._isWithActiveTrigger = function () { for (var t in this._activeTrigger) if (this._activeTrigger[t]) return !0; return !1 }, t._getConfig = function (t) { return "number" == typeof (t = l({}, this.constructor.Default, pe(this.element).data(), "object" == typeof t && t ? t : {})).delay && (t.delay = { show: t.delay, hide: t.delay }), "number" == typeof t.title && (t.title = t.title.toString()), "number" == typeof t.content && (t.content = t.content.toString()), Fn.typeCheckConfig(ve, t, this.constructor.DefaultType), t }, t._getDelegateConfig = function () { var t = {}; if (this.config) for (var e in this.config) this.constructor.Default[e] !== this.config[e] && (t[e] = this.config[e]); return t }, t._cleanTipClass = function () { var t = pe(this.getTipElement()), e = t.attr("class").match(be); null !== e && e.length && t.removeClass(e.join("")) }, t._handlePopperPlacementChange = function (t) { var e = t.instance; this.tip = e.popper, this._cleanTipClass(), this.addAttachmentClass(this._getAttachment(t.placement)) }, t._fixTransition = function () { var t = this.getTipElement(), e = this.config.animation; null === t.getAttribute("x-placement") && (pe(t).removeClass(Oe), this.config.animation = !1, this.hide(), this.show(), this.config.animation = e) }, i._jQueryInterface = function (n) { return this.each(function () { var t = pe(this).data(ye), e = "object" == typeof n && n; if ((t || !/dispose|hide/.test(n)) && (t || (t = new i(this, e), pe(this).data(ye, t)), "string" == typeof n)) { if ("undefined" == typeof t[n]) throw new TypeError('No method named "' + n + '"'); t[n]() } }) }, s(i, null, [{ key: "VERSION", get: function () { return "4.1.3" } }, { key: "Default", get: function () { return Ae } }, { key: "NAME", get: function () { return ve } }, { key: "DATA_KEY", get: function () { return ye } }, { key: "Event", get: function () { return Ne } }, { key: "EVENT_KEY", get: function () { return Ee } }, { key: "DefaultType", get: function () { return Se } }]), i }(), pe.fn[ve] = We._jQueryInterface, pe.fn[ve].Constructor = We, pe.fn[ve].noConflict = function () { return pe.fn[ve] = Ce, We._jQueryInterface }, We), Jn = (qe = "popover", Ke = "." + (Fe = "bs.popover"), Me = (Ue = e).fn[qe], Qe = "bs-popover", Be = new RegExp("(^|\\s)" + Qe + "\\S+", "g"), Ve = l({}, zn.Default, { placement: "right", trigger: "click", content: "", template: '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>' }), Ye = l({}, zn.DefaultType, { content: "(string|element|function)" }), ze = "fade", Ze = ".popover-header", Ge = ".popover-body", $e = { HIDE: "hide" + Ke, HIDDEN: "hidden" + Ke, SHOW: (Je = "show") + Ke, SHOWN: "shown" + Ke, INSERTED: "inserted" + Ke, CLICK: "click" + Ke, FOCUSIN: "focusin" + Ke, FOCUSOUT: "focusout" + Ke, MOUSEENTER: "mouseenter" + Ke, MOUSELEAVE: "mouseleave" + Ke }, Xe = function (t) { var e, n; function i() { return t.apply(this, arguments) || this } n = t, (e = i).prototype = Object.create(n.prototype), (e.prototype.constructor = e).__proto__ = n; var r = i.prototype; return r.isWithContent = function () { return this.getTitle() || this._getContent() }, r.addAttachmentClass = function (t) { Ue(this.getTipElement()).addClass(Qe + "-" + t) }, r.getTipElement = function () { return this.tip = this.tip || Ue(this.config.template)[0], this.tip }, r.setContent = function () { var t = Ue(this.getTipElement()); this.setElementContent(t.find(Ze), this.getTitle()); var e = this._getContent(); "function" == typeof e && (e = e.call(this.element)), this.setElementContent(t.find(Ge), e), t.removeClass(ze + " " + Je) }, r._getContent = function () { return this.element.getAttribute("data-content") || this.config.content }, r._cleanTipClass = function () { var t = Ue(this.getTipElement()), e = t.attr("class").match(Be); null !== e && 0 < e.length && t.removeClass(e.join("")) }, i._jQueryInterface = function (n) { return this.each(function () { var t = Ue(this).data(Fe), e = "object" == typeof n ? n : null; if ((t || !/destroy|hide/.test(n)) && (t || (t = new i(this, e), Ue(this).data(Fe, t)), "string" == typeof n)) { if ("undefined" == typeof t[n]) throw new TypeError('No method named "' + n + '"'); t[n]() } }) }, s(i, null, [{ key: "VERSION", get: function () { return "4.1.3" } }, { key: "Default", get: function () { return Ve } }, { key: "NAME", get: function () { return qe } }, { key: "DATA_KEY", get: function () { return Fe } }, { key: "Event", get: function () { return $e } }, { key: "EVENT_KEY", get: function () { return Ke } }, { key: "DefaultType", get: function () { return Ye } }]), i }(zn), Ue.fn[qe] = Xe._jQueryInterface, Ue.fn[qe].Constructor = Xe, Ue.fn[qe].noConflict = function () { return Ue.fn[qe] = Me, Xe._jQueryInterface }, Xe), Zn = (en = "scrollspy", rn = "." + (nn = "bs.scrollspy"), on = (tn = e).fn[en], sn = { offset: 10, method: "auto", target: "" }, an = { offset: "number", method: "string", target: "(string|element)" }, ln = { ACTIVATE: "activate" + rn, SCROLL: "scroll" + rn, LOAD_DATA_API: "load" + rn + ".data-api" }, cn = "dropdown-item", hn = "active", un = '[data-spy="scroll"]', fn = ".active", dn = ".nav, .list-group", gn = ".nav-link", _n = ".nav-item", mn = ".list-group-item", pn = ".dropdown", vn = ".dropdown-item", yn = ".dropdown-toggle", En = "offset", Cn = "position", Tn = function () { function n(t, e) { var n = this; this._element = t, this._scrollElement = "BODY" === t.tagName ? window : t, this._config = this._getConfig(e), this._selector = this._config.target + " " + gn + "," + this._config.target + " " + mn + "," + this._config.target + " " + vn, this._offsets = [], this._targets = [], this._activeTarget = null, this._scrollHeight = 0, tn(this._scrollElement).on(ln.SCROLL, function (t) { return n._process(t) }), this.refresh(), this._process() } var t = n.prototype; return t.refresh = function () { var e = this, t = this._scrollElement === this._scrollElement.window ? En : Cn, r = "auto" === this._config.method ? t : this._config.method, o = r === Cn ? this._getScrollTop() : 0; this._offsets = [], this._targets = [], this._scrollHeight = this._getScrollHeight(), [].slice.call(document.querySelectorAll(this._selector)).map(function (t) { var e, n = Fn.getSelectorFromElement(t); if (n && (e = document.querySelector(n)), e) { var i = e.getBoundingClientRect(); if (i.width || i.height) return [tn(e)[r]().top + o, n] } return null }).filter(function (t) { return t }).sort(function (t, e) { return t[0] - e[0] }).forEach(function (t) { e._offsets.push(t[0]), e._targets.push(t[1]) }) }, t.dispose = function () { tn.removeData(this._element, nn), tn(this._scrollElement).off(rn), this._element = null, this._scrollElement = null, this._config = null, this._selector = null, this._offsets = null, this._targets = null, this._activeTarget = null, this._scrollHeight = null }, t._getConfig = function (t) { if ("string" != typeof (t = l({}, sn, "object" == typeof t && t ? t : {})).target) { var e = tn(t.target).attr("id"); e || (e = Fn.getUID(en), tn(t.target).attr("id", e)), t.target = "#" + e } return Fn.typeCheckConfig(en, t, an), t }, t._getScrollTop = function () { return this._scrollElement === window ? this._scrollElement.pageYOffset : this._scrollElement.scrollTop }, t._getScrollHeight = function () { return this._scrollElement.scrollHeight || Math.max(document.body.scrollHeight, document.documentElement.scrollHeight) }, t._getOffsetHeight = function () { return this._scrollElement === window ? window.innerHeight : this._scrollElement.getBoundingClientRect().height }, t._process = function () { var t = this._getScrollTop() + this._config.offset, e = this._getScrollHeight(), n = this._config.offset + e - this._getOffsetHeight(); if (this._scrollHeight !== e && this.refresh(), n <= t) { var i = this._targets[this._targets.length - 1]; this._activeTarget !== i && this._activate(i) } else { if (this._activeTarget && t < this._offsets[0] && 0 < this._offsets[0]) return this._activeTarget = null, void this._clear(); for (var r = this._offsets.length; r--;) { this._activeTarget !== this._targets[r] && t >= this._offsets[r] && ("undefined" == typeof this._offsets[r + 1] || t < this._offsets[r + 1]) && this._activate(this._targets[r]) } } }, t._activate = function (e) { this._activeTarget = e, this._clear(); var t = this._selector.split(","); t = t.map(function (t) { return t + '[data-target="' + e + '"],' + t + '[href="' + e + '"]' }); var n = tn([].slice.call(document.querySelectorAll(t.join(",")))); n.hasClass(cn) ? (n.closest(pn).find(yn).addClass(hn), n.addClass(hn)) : (n.addClass(hn), n.parents(dn).prev(gn + ", " + mn).addClass(hn), n.parents(dn).prev(_n).children(gn).addClass(hn)), tn(this._scrollElement).trigger(ln.ACTIVATE, { relatedTarget: e }) }, t._clear = function () { var t = [].slice.call(document.querySelectorAll(this._selector)); tn(t).filter(fn).removeClass(hn) }, n._jQueryInterface = function (e) { return this.each(function () { var t = tn(this).data(nn); if (t || (t = new n(this, "object" == typeof e && e), tn(this).data(nn, t)), "string" == typeof e) { if ("undefined" == typeof t[e]) throw new TypeError('No method named "' + e + '"'); t[e]() } }) }, s(n, null, [{ key: "VERSION", get: function () { return "4.1.3" } }, { key: "Default", get: function () { return sn } }]), n }(), tn(window).on(ln.LOAD_DATA_API, function () { for (var t = [].slice.call(document.querySelectorAll(un)), e = t.length; e--;) { var n = tn(t[e]); Tn._jQueryInterface.call(n, n.data()) } }), tn.fn[en] = Tn._jQueryInterface, tn.fn[en].Constructor = Tn, tn.fn[en].noConflict = function () { return tn.fn[en] = on, Tn._jQueryInterface }, Tn), Gn = (In = "." + (Sn = "bs.tab"), An = (bn = e).fn.tab, Dn = { HIDE: "hide" + In, HIDDEN: "hidden" + In, SHOW: "show" + In, SHOWN: "shown" + In, CLICK_DATA_API: "click" + In + ".data-api" }, wn = "dropdown-menu", Nn = "active", On = "disabled", kn = "fade", Pn = "show", jn = ".dropdown", Hn = ".nav, .list-group", Ln = ".active", Rn = "> li > .active", xn = '[data-toggle="tab"], [data-toggle="pill"], [data-toggle="list"]', Wn = ".dropdown-toggle", Un = "> .dropdown-menu .active", qn = function () { function i(t) { this._element = t } var t = i.prototype; return t.show = function () { var n = this; if (!(this._element.parentNode && this._element.parentNode.nodeType === Node.ELEMENT_NODE && bn(this._element).hasClass(Nn) || bn(this._element).hasClass(On))) { var t, i, e = bn(this._element).closest(Hn)[0], r = Fn.getSelectorFromElement(this._element); if (e) { var o = "UL" === e.nodeName ? Rn : Ln; i = (i = bn.makeArray(bn(e).find(o)))[i.length - 1] } var s = bn.Event(Dn.HIDE, { relatedTarget: this._element }), a = bn.Event(Dn.SHOW, { relatedTarget: i }); if (i && bn(i).trigger(s), bn(this._element).trigger(a), !a.isDefaultPrevented() && !s.isDefaultPrevented()) { r && (t = document.querySelector(r)), this._activate(this._element, e); var l = function () { var t = bn.Event(Dn.HIDDEN, { relatedTarget: n._element }), e = bn.Event(Dn.SHOWN, { relatedTarget: i }); bn(i).trigger(t), bn(n._element).trigger(e) }; t ? this._activate(t, t.parentNode, l) : l() } } }, t.dispose = function () { bn.removeData(this._element, Sn), this._element = null }, t._activate = function (t, e, n) { var i = this, r = ("UL" === e.nodeName ? bn(e).find(Rn) : bn(e).children(Ln))[0], o = n && r && bn(r).hasClass(kn), s = function () { return i._transitionComplete(t, r, n) }; if (r && o) { var a = Fn.getTransitionDurationFromElement(r); bn(r).one(Fn.TRANSITION_END, s).emulateTransitionEnd(a) } else s() }, t._transitionComplete = function (t, e, n) { if (e) { bn(e).removeClass(Pn + " " + Nn); var i = bn(e.parentNode).find(Un)[0]; i && bn(i).removeClass(Nn), "tab" === e.getAttribute("role") && e.setAttribute("aria-selected", !1) } if (bn(t).addClass(Nn), "tab" === t.getAttribute("role") && t.setAttribute("aria-selected", !0), Fn.reflow(t), bn(t).addClass(Pn), t.parentNode && bn(t.parentNode).hasClass(wn)) { var r = bn(t).closest(jn)[0]; if (r) { var o = [].slice.call(r.querySelectorAll(Wn)); bn(o).addClass(Nn) } t.setAttribute("aria-expanded", !0) } n && n() }, i._jQueryInterface = function (n) { return this.each(function () { var t = bn(this), e = t.data(Sn); if (e || (e = new i(this), t.data(Sn, e)), "string" == typeof n) { if ("undefined" == typeof e[n]) throw new TypeError('No method named "' + n + '"'); e[n]() } }) }, s(i, null, [{ key: "VERSION", get: function () { return "4.1.3" } }]), i }(), bn(document).on(Dn.CLICK_DATA_API, xn, function (t) { t.preventDefault(), qn._jQueryInterface.call(bn(this), "show") }), bn.fn.tab = qn._jQueryInterface, bn.fn.tab.Constructor = qn, bn.fn.tab.noConflict = function () { return bn.fn.tab = An, qn._jQueryInterface }, qn); !function (t) { if ("undefined" == typeof t) throw new TypeError("Bootstrap's JavaScript requires jQuery. jQuery must be included before Bootstrap's JavaScript."); var e = t.fn.jquery.split(" ")[0].split("."); if (e[0] < 2 && e[1] < 9 || 1 === e[0] && 9 === e[1] && e[2] < 1 || 4 <= e[0]) throw new Error("Bootstrap's JavaScript requires at least jQuery v1.9.1 but less than v4.0.0") }(e), t.Util = Fn, t.Alert = Kn, t.Button = Mn, t.Carousel = Qn, t.Collapse = Bn, t.Dropdown = Vn, t.Modal = Yn, t.Popover = Jn, t.Scrollspy = Zn, t.Tab = Gn, t.Tooltip = zn, Object.defineProperty(t, "__esModule", { value: !0 }) });
//# sourceMappingURL=bootstrap.min.js.map
// =======================================================================================================





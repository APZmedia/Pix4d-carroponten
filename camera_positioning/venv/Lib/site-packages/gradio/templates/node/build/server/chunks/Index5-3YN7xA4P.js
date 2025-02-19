import { c as create_ssr_component, v as validate_component } from './ssr-e_x9MT2V.js';
import { B as Block } from './2-BlNe9qkL.js';
import './index-C752EedE.js';
import 'tty';
import 'path';
import 'url';
import 'fs';
import './Component-DtWdek5W.js';

const Index = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { elem_id } = $$props;
  let { elem_classes } = $$props;
  let { visible = true } = $$props;
  if ($$props.elem_id === void 0 && $$bindings.elem_id && elem_id !== void 0)
    $$bindings.elem_id(elem_id);
  if ($$props.elem_classes === void 0 && $$bindings.elem_classes && elem_classes !== void 0)
    $$bindings.elem_classes(elem_classes);
  if ($$props.visible === void 0 && $$bindings.visible && visible !== void 0)
    $$bindings.visible(visible);
  return `${validate_component(Block, "Block").$$render(
    $$result,
    {
      elem_id,
      elem_classes,
      visible,
      explicit_call: true
    },
    {},
    {
      default: () => {
        return `${slots.default ? slots.default({}) : ``}`;
      }
    }
  )}`;
});

export { Index as default };
//# sourceMappingURL=Index5-3YN7xA4P.js.map

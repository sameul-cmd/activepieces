import { createAction, createPiece, PieceAuth, Property } from '@activepieces/pieces-framework';

const sayHello = createAction({
  name: 'say_hello',
  displayName: 'Say hello',
  description: 'Returns a greeting (Phase 0 custom piece test).',
  props: {
    name: Property.ShortText({ displayName: 'Name', required: true }),
  },
  async run(context) {
    return { message: `Hello ${context.propsValue.name} from a custom piece` };
  },
});

export const p0Hello = createPiece({
  displayName: 'P0 Hello',
  description: 'Phase 0 test piece',
  auth: PieceAuth.None(),
  minimumSupportedRelease: '0.36.1',
  logoUrl: 'https://cdn.activepieces.com/pieces/http.png',
  authors: [],
  actions: [sayHello],
  triggers: [],
});

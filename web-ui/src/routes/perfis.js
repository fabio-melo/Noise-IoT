import React from 'react';

import {
  Create,
  Edit,
  ReferenceArrayField,
  TabbedForm,
  FormTab,
  TextInput,
  ChipField,
  SingleFieldList,
  List,
  Datagrid,
  TextField,
  ArrayInput,
  SimpleFormIterator,
  BooleanInput,
  FormDataConsumer,
  SelectInput,
  DateField,
  ImageField,
  Show,
  SimpleShowLayout,
  required
} from 'react-admin';

import { Actions, validateTitle } from '../config';
import { withStyles } from '@material-ui/core/styles';

const styles = {
  image: { maxHeight: '3rem' },
  stock: { width: '5em' },
  price: { width: '5em' },
  width: { width: '5em' },
  widthFormGroup: { display: 'inline-block' },
  height: { width: '5em' },
  heightFormGroup: { display: 'inline-block', marginLeft: 32 },
  linkredes: { width: '50em' },
  linkredesFormGroup: { display: 'inline-block', marginLeft: 32 }

};

export const PerfList = withStyles(styles)(({ classes, permissions, ...props }) => (
  <List title="Segurança" {...props} actions={<Actions />}>
    <Datagrid rowClick="show">
      <TextField source="device_id" label="ID do Dispositivo" />			
      <DateField source="time" label="Data e Hora do Evento" showTime />
      <ImageField source="image" title="image" />

    </Datagrid>
  </List>
));

export const PerfShow = withStyles(styles)(({ classes, permissions, ...props }) => (
  <Show title="Segurança" {...props} actions={<Actions />}>
    <SimpleShowLayout>
      <TextField source="device_id" label="ID do Dispositivo" />			
      <DateField source="time" label="Data e Hora do Evento" showTime />
      <ImageField source="image" title="image" />

    </SimpleShowLayout>
  </Show>
));


